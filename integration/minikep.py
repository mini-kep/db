# TODO: bring list from README.md

"""Access functions/classes for: 
    - api/freq: get_freq() 
    - api/names/{freq}: get_names(freq) 
    - api/info/?name={name}: VarInfo
    - api/datapoints: DatapointsCSV, DatapointsJSON 
    - api/frame: Frame
    - custom API: CustomAPI
    
"""

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
    assert Caller('api/print', dict(a=1)).url == \
        'http://minikep-db.herokuapp.com/api/print?a=1'
    assert Caller('api/print').url == 'http://minikep-db.herokuapp.com/api/print'   

    assert datapoints(freq='a', name='GDP_yoy')
    assert series(freq='a', name='GDP_yoy')
    
    vi = VarInfo(freq='a', name='GDP_yoy')
    assert vi.start_date 
    assert vi.latest_date 
    assert vi.latest_value 

    c_api = CustomAPI('ru/series/GDP_yoy/a')
    assert c_api.endpoint 
    assert c_api.url 
    assert c_api.text()
    
    assert CustomAPI('ru/series/GDP_yoy/a').text() == \
           series(freq='a', name='GDP_yoy')
