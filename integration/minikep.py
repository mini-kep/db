"""Wrappers for API methods:
    
   - api/freq
   - api/names
   - api/info
   - api/datapoints
   - api/series
   - api/frame
   - custom api

   
"""


# NOT TODO:
#  1. google-style <https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments>
#     docstrings for methods/classes above:
#       a) write most sensistive part of docstring - something less clear
#       b) rest fo docstrings
#  2. make unitttests
#       a) extend asserts in __main__ section
#       b) convert to unittests

# NOTE: Safety feature when no name is selected (in frontend)
#
#    def json(self):
#        data = requests.get(self.url).json()
#        # if parameters are invalid, response is not a list
#        if not isinstance(data, list):
#            return []
#        return data

import pandas as pd
import requests
from urllib.parse import urlencode, urlunparse, ParseResult


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

















class Caller:

    def __init__(self, endpoint, param_dict={}, base=BASE_URL):
        self.base = base
        self.param_dict = param_dict
        self.endpoint = endpoint

    @property
    def url(self):
        pr = ParseResult(scheme='http',
                         netloc=self.base,
                         path=self.endpoint,
                         params=None,
                         query=urlencode(self.param_dict),
                         fragment=None)
        return urlunparse(pr)

    def response(self):
        return requests.get(self.url)

    def json(self):
        return self.response().json()

    def text(self):
        return self.response().text


def make_dict(**kwargs):
    for key in ('start_date', 'end_date'):
        if key in kwargs.keys() and not kwargs.get(key):
            del kwargs[key]
    return kwargs


assert make_dict(a=1) == {'a': 1}
assert make_dict(start_date=1) == {'start_date': 1}
assert make_dict(start_date=None) == {}

# API access methods:


def freq():
    return Caller('api/freq').json()


def names(freq):
    endpoint = 'api/names/{}'.format(freq)
    return Caller(endpoint).json()


def info(name, freq):
    # TODO: simplify API, call by 'name' only
    param = make_dict(name=name, freq=freq)
    return Caller('api/info', param).json()


def datapoints(freq, name, start_date=None, end_date=None):
    param = make_dict(freq=freq, name=name,
                      start_date=start_date, end_date=end_date)
    return Caller('api/datapoints', param).json()


def series(freq, name, start_date=None, end_date=None):
    param = make_dict(freq=freq, name=name,
                      start_date=start_date, end_date=end_date)
    return Caller('api/series', param).text()


def frame(freq, names, start_date=None, end_date=None):
    param = make_dict(freq=freq, names=names,
                      start_date=start_date, end_date=end_date)
    return Caller('api/frame', param).text()


class CustomAPI:
    def __init__(self, freq, name):
        # FIXME: this is not always 'ru'
        self.endpoint = 'ru/series/{}/{}'.format(name, freq)

    @property
    def url(self):
        return Caller(self.endpoint).url
    
    @property
    def data(self):
        return Caller(self.endpoint).text()


def get_frame_url(freq, names, start_date=None, end_date=None):
    param = make_dict(freq=freq, names=','.join(names),
                      start_date=start_date, end_date=end_date)
    return Caller('api/frame', param).url


class VarInfo:
    """Convenience class to get info about variable"""

    def __init__(self, freq, name):
        self.freq = freq
        self.info = info(name, freq)

    def __getattr__(self, x):
        return self.info[self.freq].get(x)


if __name__ == '__main__':
#    assert Caller('api/print', dict(a=1)).url == \
#        'http://minikep-db.herokuapp.com/api/print?a=1'
#    assert Caller(
#        'api/print').url == 'http://minikep-db.herokuapp.com/api/print'
#
#    assert datapoints(freq='a', name='GDP_yoy')
#    assert series(freq='a', name='GDP_yoy')
#
#    vi = VarInfo(freq='a', name='GDP_yoy')
#    assert vi.start_date
#    assert vi.latest_date
#    assert vi.latest_value
#
#    c_api = CustomAPI('GDP_yoy', 'a')
#    assert c_api.endpoint
#    assert c_api.url
#
#    assert CustomAPI('a', 'GDP_yoy').data == series(freq='a', name='GDP_yoy')
