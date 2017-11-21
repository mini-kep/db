# Custom API

Custom API provides a more user-friendly syntax for ```GET \api\datapoints```, 
as described [here](https://mini-kep.github.io/documentation/custom_api/). 

For example, quickstart link for GDP growth rates can be shortened to:

<https://minikep-db.herokuapp.com/ru/series/GDP_yoy/q/2016-01-01>

Custom API is experimental and not guaranteed now. 

#### URL syntax

From [custom_api.py docstring](https://github.com/mini-kep/db/blob/master/db/custom_api/custom_api.py#L1-L36):

```
URL format (? marks optional parameter):

    {domain}/series/{varname}/{freq}/{?suffix}/{?start}/{?end}/{?finaliser}
    
    
	
Tokens:
	{domain} is reserved, future use: 'all', 'ru', 'oil', 'ru:bank', 'ru:77'
	
	{varname} is GDP, GOODS_EXPORT, BRENT (capital letters with underscores)
	
	{freq} is any of:
	    a (annual)
	    q (quarterly)
	    m (monthly)
	    w (weekly)
	    d (daily)
	
	{?suffix} may be:
	
	unit of measurement (unit):
		example: bln_rub, bln_usd, tkm
	
	rate of change for real variable (rate):
		rog - change to previous period
		yoy - change to year ago
		base - base index
	
	aggregation command (agg):
		eop - end of period
		avg - average
```		


#### Example calls

- basic calls:
    - [/ru/series/GDP/a/yoy/1998/2017](http://minikep-db.herokuapp.com/ru/series/GDP/a/yoy/1998/2017)
    - [ru/series/EXPORT_GOODS/m/bln_rub](http://minikep-db.herokuapp.com/ru/series/EXPORT_GOODS/m/bln_rub)
    
- units positioning:
    - [/ru/series/CPI_rog/m/2000/2010)](http://minikep-db.herokuapp.com/ru/series/CPI_rog/m/2000/2010)
    - [/ru/series/CPI/m/rog/2000/2010](http://minikep-db.herokuapp.com/ru/series/CPI/m/rog/2000/2010)
    - [/ru/series/CP/m/2016/rog](https://minikep-db.herokuapp.com/ru/series/CPI/m/2016/rog)

- no unit:
    - [/ru/series/USDRUR_CB/d/2000/2001](https://minikep-db.herokuapp.com/ru/series/USDRUR_CB/d/2015/2016)

- reserved domain:
    - [/oil/series/BRENT/d/2017](https://minikep-db.herokuapp.com/oil/series/BRENT/d/2017)
    

#### User code

```python
import pandas as pd

def read_ts(source_url):
	"""Read pandas time series from *source_url*."""
	return pd.read_csv(source_url, 
                      converters={0: pd.to_datetime}, 
                      index_col=0,
                      squeeze=True)

er = read_ts('http://minikep-db.herokuapp.com/ru/series/USDRUR_CB/d/2017/')

assert er['2017-09-28'] == 58.01022
```
