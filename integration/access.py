import requests
import pandas as pd

"""
- api/freq
- api/names
- api/info
- api/datapoints
- api/frame
- custom api
"""

BASE_URL = 'http://minikep-db.herokuapp.com/'


def fetch_json(url):
    return requests.get(url).json()


def get_freq():
    url = BASE_URL + 'api/freq'
    return fetch_json(url)


def get_names(freq):
    url = BASE_URL + 'api/names/{}'.format(freq)
    return fetch_json(url)

# TODO: must simplify this callto 'api/info?name={}', make freq optional


def get_info(freq, name):
    url = BASE_URL + 'api/info?freq={}&name={}'.format(freq, name)
    return fetch_json(url)


def make_params(freq, name, start_date=None, end_date=None):
    s = '?name={}&freq={}'.format(name, freq)
    if start_date:
        s += '&start_date={}'.format(start_date)
    if end_date:
        s += '&end_date={}'.format(end_date)
    return s


def make_datapoints_url(freq, name, start_date=None, end_date=None):
    return BASE_URL + 'api/datapoints' + \
        make_params(freq, name, start_date, end_date)


def make_series_url(freq, name, start_date=None, end_date=None):
    url = BASE_URL + 'api/series' + \
        make_params(freq, name, start_date, end_date)


def get_datapoints_json(freq, name, start_date=None, end_date=None):
    url = make_datapoints_url(freq, name, start_date, end_date)
    return fetch_json(url)


def get_ts(freq, name, start_date=None, end_date=None):
    url = make_series_url(freq, name, start_date=start_date, end_date=end_date)
    return read_ts_from_url(url)


def get_frame(freq):
    url = BASE_URL + f'api/frame?freq={freq}'
    return read_df_from_url(url)

# TODO: add finaliser


def get_custom_series(freq, name, suffix, start, end, domain='ru'):
    url = BASE_URL + f'{domain}/series/{name}/{freq}/{suffix}/{start}/{end}'
    return read_ts_from_url(url)

# pandas series and dataframes


def read_ts_from_url(url):
    """Read pandas time series from *source_url*."""
    return pd.read_csv(url, converters={0: pd.to_datetime}, index_col=0,
                       squeeze=True)


def read_df_from_url(url):
    """Read pandas dataframe from *source_url*."""
    return pd.read_csv(url, converters={0: pd.to_datetime}, index_col=0)

# supplements for checks


def join_df(df_list):
    df = df_list[0]
    for right_df in df_list[1:]:
        df = df.join(right_df, how='outer')
    return df


def get_df_by_names(freq, names):
    df_list = [get_ts(freq, name).to_frame() for name in names]
    return join_df(df_list)


# TODO: check this is equal to get_frame()
def get_df(freq):
    names = get_names(freq)
    return get_df_by_names(freq, names)


if __name__ == '__main__':
    # get variable list for frequency 'q' (quarterly)
    variable_names_quarterly = get_names('q')
    # read one variable as pd.Series
    ts = get_ts('q', 'GDP_yoy')
    # read all variables for frequency 'q' as pd.DataFrame
    # runs about 20-40 sec
    dfq = get_df('q')
    # check dataframe columns are exaactly the ones we retrieved earlier
    assert variable_names_quarterly == dfq.columns.tolist()
