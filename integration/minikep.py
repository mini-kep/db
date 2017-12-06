"""Access functions/classes for: 
    - api/freq: get_freq() 
    - api/names/{freq}: get_names(freq) 
    - api/info/?name={name}: VarInfo
    - api/datapoints: DatapointsCSV, DatapointsJSON 
    - api/frame: Frame
    - custom API: CustomAPI
    
"""

# TODO: Refactoring, involving API change
# 1. Datapoints should have no format, just json both for input and output
# 2. csv for one variable should be read at new endpoint 'api/series?freq=a&name=GDP_yoy'
# 3. changes should be reflected in 'db' repo tests + in readme.md + at api_requests.py

#NOT TODO:
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

import requests
from urllib.parse import urlencode, urlunparse, ParseResult

BASE_URL = 'minikep-db.herokuapp.com'

class Caller:
    
    def __init__(self, endpoint, param_dict={}, base=BASE_URL):
        self.base = base
        self.param_dict = param_dict
        self.endpoint = endpoint

    @property 
    def url(self):
        param_str = urlencode(self.param_dict)
        pr = ParseResult(scheme='http', 
                        netloc=self.base, 
                        path=self.endpoint, 
                        params=None,  
                        query=param_str, 
                        fragment=None)
        return urlunparse(pr)  

    def response(self):
        return requests.get(self.url)          
        
    def json(self):
        return self.response().json()
    
    def text(self):
        return self.response().text


class Parameters:
    def __init__(self, freq):
        self.dict = dict(freq=freq)
        
    def _add(self, key, value):
        if value:
            self.dict[key]=value
    
    def add_name(self, value):
        self._add('name', value)
    
    def add_names(self, value):
        self._add('names', value)

    def add_dates(self, start_date, end_date):
        self._add('start_date', start_date)
        self._add('end_date', end_date)
        

def make_dict(freq, name, start_date, end_date):
    param = Parameters(freq)
    param.add_name(name)
    param.add_dates(start_date, end_date)
    return param.dict
    
class MiniKEP:

    def freq():
        return Caller('api/freq').json()    
    
    def names(freq):
        endpoint = 'api/names/{}'.format(freq)
        return Caller(endpoint).json()

    def info(name, freq):
        # TODO: simplify API, call by 'name' only
        param = Parameters(freq)
        param.add_name(name)
        return Caller('api/info', param.dict).json()
    
    #TODO: with api shange this should be datapoints()
    def datapoints_json(freq, name, start_date=None, end_date=None):
        param_dict = make_dict(freq, name, start_date, end_date)
        return Caller('api/datapoints', param_dict).json()

    #TODO: with api shange this should be series()
    def datapoints_csv(freq, name, start_date=None, end_date=None):
        param_dict = make_dict(freq, name, start_date, end_date)
        return Caller('api/series', param_dict).text()

    def frame(freq, names, start_date=None, end_date=None):
        param = Parameters(freq)
        param.add_names(names)
        param.add_dates(start_date, end_date)
        return Caller('api/frame', param.dict).text()        

class CustomAPI:
    def __init__(self, inner_str):
        self.endpoint = inner_str

    @property
    def url(self):
        return Caller(self.endpoint).url

    def text(self):
        return Caller(self.endpoint).text()

class VarInfo:
    """Convenience class to get info about variable"""
    def __init__(self, freq, name):
        self.freq = freq
        self.info = MiniKEP.info(name, freq)
        
    def __getattr__(self, x):
        return self.info[self.freq].get(x)

if __name__ == '__main__': 
    assert Caller('api/print', dict(a=1)).url == \
        'http://minikep-db.herokuapp.com/api/print?a=1'
    assert Caller('api/print').url == 'http://minikep-db.herokuapp.com/api/print'   

    assert MiniKEP.datapoints_json(freq='a', name='GDP_yoy')
    assert MiniKEP.datapoints_csv(freq='a', name='GDP_yoy')
    
    vi = VarInfo(freq='a', name='GDP_yoy')
    assert vi.start_date 
    assert vi.latest_date 
    assert vi.latest_value 

    c_api = CustomAPI('ru/series/GDP_yoy/a')
    assert c_api.endpoint 
    assert c_api.url 
    assert c_api.text()
    
    assert CustomAPI('ru/series/GDP_yoy/a').text() == \
MiniKEP.datapoints_csv(freq='a', name='GDP_yoy')
