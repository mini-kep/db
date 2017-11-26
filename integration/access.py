import requests
import pandas as pd


def fetch_json(url):
    return requests.get(url).json()

def get_freq():
    url = 'http://minikep-db.herokuapp.com/api/freq'
    return fetch_json(url)


def get_names(freq):
    url = 'http://minikep-db.herokuapp.com/api/names/{}'.format(freq)
    return fetch_json(url)


def get_info(freq, name):
    url = 'http://minikep-db.herokuapp.com/api/info?freq={}&name={}'.format(freq, name)
    return fetch_json(url)


def make_url(freq, name, format, start_date=None, end_date=None):

    base_url = ('https://minikep-db.herokuapp.com/api/datapoints'
            '?name={}&freq={}&format={}'.format(name, freq, format))

    if start_date or end_date:
        return base_url + '&start_date={}&end_date={}'.format(start_date, end_date)
    return base_url


def get_datapoints(freq, name, format='json', start_date=None, end_date=None):
    url = make_url(freq, name, format, start_date, end_date)
    if format == 'csv':
        return read_from_url(url)
    return fetch_json(url)


def get_datapoints_full_response(freq, name, start_date=None, end_date=None):
    url = make_url(freq, name, 'csv', start_date=start_date, end_date=end_date)
    return requests.get(url)


def read_from_url(url):
    """Read pandas time series from *source_url*."""
    return pd.read_csv(url, converters={0: pd.to_datetime}, index_col=0, squeeze=True)


def get_ts(freq, name, start_date=None, end_date=None):
    url = make_url(freq, name, 'csv', start_date=start_date, end_date=end_date)
    return read_from_url(url)


def join_df(df_list):
    df = df_list[0]
    for right_df in df_list[1:]:
        df = df.join(right_df, how='outer')
    return df

def get_df_by_names(freq, names):
    df_list = [get_ts(freq, name).to_frame() for name in names]
    return join_df(df_list)


def get_df(freq):
    names = get_names(freq)
    return get_df_by_names(freq, names)

def get_custom_series(freq, name, suffix, start, end):
    url = f'http://mini-kep.herokuapp.com/ru/series/{name}/{freq}/{suffix}/{start}/{end}'
    return read_from_url(url)


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
    
#        Index(['CPI_ALCOHOL_rog', 'CPI_FOOD_rog', 'CPI_NONFOOD_rog', 'CPI_rog',
#               'CPI_SERVICES_rog', 'EXPORT_GOODS_bln_usd', 'GDP_bln_rub', 'GDP_yoy',
#               'GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub',
#               'GOV_EXPENSE_ACCUM_FEDERAL_bln_rub',
#               'GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub',
#               'GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub',
#               'GOV_REVENUE_ACCUM_FEDERAL_bln_rub',
#               'GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub',
#               'GOV_SURPLUS_ACCUM_FEDERAL_bln_rub',
#               'GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub', 'IMPORT_GOODS_bln_usd',
#               'INDPRO_rog', 'INDPRO_yoy', 'INVESTMENT_bln_rub', 'INVESTMENT_rog',
#               'INVESTMENT_yoy', 'RETAIL_SALES_bln_rub', 'RETAIL_SALES_FOOD_bln_rub',
#               'RETAIL_SALES_FOOD_rog', 'RETAIL_SALES_FOOD_yoy',
#               'RETAIL_SALES_NONFOOD_bln_rub', 'RETAIL_SALES_NONFOOD_rog',
#               'RETAIL_SALES_NONFOOD_yoy', 'RETAIL_SALES_rog', 'RETAIL_SALES_yoy',
#               'TRANSPORT_FREIGHT_bln_tkm', 'UNEMPL_pct', 'WAGE_NOMINAL_rub',
#               'WAGE_REAL_rog', 'WAGE_REAL_yoy'],
#              dtype='object')

    # can also get monthly data
    # commented because it slows down code, uncomment if you need monthly data
    # dfm = get_df('m')    
