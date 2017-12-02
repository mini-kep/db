"""Access functions/classes for: 
    - api/freq: get_freq() 
    - api/names/{freq}: get_names(freq) 
    - api/info/?name={name}: VarInfo
    - api/datapoints: DatapointsCSV, DatapointsJSON 
    - api/frame: Frame
    - custom API: CustomAPI
    
"""

#TODO:
#  1. google-style <https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments>
#     docstrings for methods/classes above:
#       a) write most sensistive part of docstring - something less clear
#       b) rest fo docstrings          
#  2. make unitttests
#       a) extend asserts in __main__ section       
#       b) convert to unittests


import requests
from urllib.parse import urlencode, urlunparse, ParseResult

BASE_URL = 'minikep-db.herokuapp.com'
   
def make_url(endpoint: str, param_dict: dict = {}, base=BASE_URL):
    param_str = urlencode(param_dict)
    pr = ParseResult(scheme='http', 
                    netloc=base, 
                    path=endpoint, 
                    params=None,  
                    query=param_str, 
                    fragment=None)
    return urlunparse(pr)    

   
def fetch_json(url):
    data = requests.get(url).json()
    # if parameters are invalid, response is not a list
    # if not isinstance(data, list):
    #    return []
    return data


def get(endpoint, param_dict={}):
    url = make_url(endpoint, param_dict)
    data = fetch_json(url)
    if not isinstance(data, list):
        return []
    return data


def get_freq():
    return get('api/freq')


def get_names(freq):
    endpoint = 'api/names/{}'.format(freq)
    return get(endpoint)


class ParameterBase(object):
    endpoint = ''

    def __init__(self, **kwargs):
        self.param_dict = kwargs

    @property
    def url(self):
        return make_url(self.endpoint, self.param_dict)

    def json(self):
        data = requests.get(self.url).json()
        # if parameters are invalid, response is not a list
        if not isinstance(data, list):
            return []
        return data

    def text(self):
        return requests.get(self.url).text


class DatapointsJSON(ParameterBase):
    endpoint = 'api/datapoints'

    def __init__(self, freq, name):
        super().__init__(freq = freq, name = name, format = 'json')


class DatapointsCSV(ParameterBase):
    endpoint = 'api/datapoints'

    def __init__(self, freq, name):
        super().__init__(freq = freq, name = name, format = 'csv')


class Frame(ParameterBase):
    endpoint = 'api/frame'
    def __init__(self, freq, names):        
        super().__init__(freq = freq, names = ','.join(names))


class VarInfo:
    def __init__(self, freq, name):
        self.freq = freq
        url = make_url('api/info', {'freq': freq, 'name': name})
        self.info = fetch_json(url)

    def __getattr__(self, x):
        return self.info[self.freq].get(x)


class CustomAPI:
    def __init__(self, freq, name, domain='ru'):
        self._endpoint = f'{domain}/series/{name}/{freq}'

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def url(self):
        return make_url(self.endpoint)

    def text(self):
        return requests.get(self.url).text


if __name__ == '__main__': 
    assert make_url('api/print', dict(a=1)) == \
        'http://minikep-db.herokuapp.com/api/print?a=1'
    assert make_url('api/print') == 'http://minikep-db.herokuapp.com/api/print'   

    # TODO: add more specific checks
    assert DatapointsCSV(freq='a', name='GDP_yoy').url
    assert DatapointsCSV(freq='a', name='GDP_yoy').text()
    assert DatapointsJSON(freq='a', name='GDP_yoy').url
    assert DatapointsJSON(freq='a', name='GDP_yoy').json() 
    
    vi = VarInfo(freq='a', name='GDP_yoy')
    assert vi.start_date 
    assert vi.latest_date 
    assert vi.latest_value 
    assert CustomAPI(domain='ru', freq='a', name='GDP_yoy').endpoint 
    assert CustomAPI(domain='ru', freq='a', name='GDP_yoy').url 
    assert CustomAPI(freq='a', name='GDP_yoy').endpoint 
    assert CustomAPI(freq='a', name='GDP_yoy').url 
    assert CustomAPI(freq='a', name='GDP_yoy').text()
    assert CustomAPI(freq='d', name='BRENT', domain='oil').url 
    
    assert CustomAPI(freq='a', name='GDP_yoy').text() == \
DatapointsCSV(freq='a', name='GDP_yoy').text()