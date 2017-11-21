[![Build Status](https://travis-ci.org/mini-kep/db.svg?branch=master)](https://travis-ci.org/mini-kep/db)
[![Assertible status](https://assertible.com/apis/56e34b07-ae3a-4248-937e-fef69d8ec2f2/status?api_token=VkiQoHOdjWU3vGv2)](https://assertible.com/dashboard#/services/56e34b07-ae3a-4248-937e-fef69d8ec2f2/results)
[![Coverage badge](https://codecov.io/gh/mini-kep/db/branch/master/graphs/badge.svg)](https://codecov.io/gh/mini-kep/db)

# Quickstart

You can query macroeconomic database by indicator name, frequency (from annual to daily) and date range. 

Link below will provide quarterly year-on-year Russian GDP growth rates as csv file, readable by R/pandas:

<https://minikep-db.herokuapp.com/api/datapoints?name=GDP_yoy&freq=q&start_date=2016-01-01>

```
,GDP_yoy
2016-03-31,99.6
2016-06-30,99.5
2016-09-30,99.6
2016-12-31,100.3
2017-03-31,100.5
2017-06-30,102.5
```

R/pandas code to access this data is [here](https://github.com/mini-kep/user-charts/blob/master/access.py).

```api/datapoints``` also allows to upload and delete datapoints with API token. This functionality 
is used by administrator and scheduled [parsers](https://github.com/mini-kep/parsers).

Additional endpoints to navigate this dataset are:

  - ```api/freq``` - list avalable frequencies
  - ```api/names/{freq}``` - list variable names under specified frequency 
  - ```api/info/?name={name}``` - provide additional information about a variable


# API description 

Initial specification for database API is [here](https://mini-kep.github.io/documentation/database/),
updates are documented below.

See also experimental [Swagger documentation](http://minikep-db.herokuapp.com/apidocs). 


#### GET ```freq```:

List avalable frequencies in the dataset. Returns ```{'a', 'q', 'm', 'd'}```.

- [api/freq](https://minikep-db.herokuapp.com/api/freq)


#### GET ```names```:

List variable names for specified frequency.

- [api/names/a](https://minikep-db.herokuapp.com/api/names/a)
- [api/names/q](https://minikep-db.herokuapp.com/api/names/q)
- [api/names/m](https://minikep-db.herokuapp.com/api/names/m)
- [api/names/d](https://minikep-db.herokuapp.com/api/names/d)

#### GET ```datapoints```:

Get subset of data as csv or json.

- [api/datapoints?name=CPI_rog&freq=m](https://minikep-db.herokuapp.com/api/datapoints?name=CPI_rog&freq=m)
- [api/datapoints?name=GDP_yoy&freq=q](https://minikep-db.herokuapp.com/api/datapoints?name=GDP_yoy&freq=q)
- [api/datapoints?name=BRENT&freq=d&start_date=2017-01-01](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2017-01-01)
- [api/datapoints?name=USDRUR_CB&freq=d&start_date=2017-08-01&end_date=2017-10-01](https://minikep-db.herokuapp.com/api/datapoints?name=USDRUR_CB&freq=d&start_date=2017-08-01&end_date=2017-10-01)


#### GET ```frame```
Returns a csv dataframe.

Example call:

<http://minikep-db.herokuapp.com/api/frame?freq=d&names=BRENT,USDRUR_CB&start_date=2017-10-01&end_date=2017-10-10>
```,BRENT,USDRUR_CB
2017-10-02,55.67,
2017-10-03,56.12,57.8134
2017-10-04,56.0,57.9375
2017-10-05,57.09,57.7832
2017-10-06,55.5,57.5811
2017-10-07,,57.7612
2017-10-09,55.29,
2017-10-10,56.62,58.3151
```
If there's no data for specified name and date, value will be skipped. You can see it in example above - `2017-10-07,,57.7612`

Required params:
- `freq` - one of ```{'a', 'q', 'm', 'd'}```

Optional params:
- `names` - one or multiplie names (separated by comma). If not specified, then a dataframe with all avaibalive names will be returned. Available names could be listed via `GET names`.
- `start_date` - starting date for data, like `2017-10-25`.
- `end_date` - ending date for data, like `2018-03-20`.

Examples:
- [api/frame?freq=a](http://minikep-db.herokuapp.com/api/frame?freq=a)
- [api/frame?freq=m&names=CPI_rog,CPI_SERVICES_rog](http://minikep-db.herokuapp.com/api/frame?freq=m&names=CPI_rog,CPI_SERVICES_rog)
- [api/frame?freq=q&names=CPI_FOOD_rog,CPI_ALCOHOL_rog&start_date=2015-01-01](http://minikep-db.herokuapp.com/api/frame?freq=q&names=CPI_FOOD_rog,CPI_ALCOHOL_rog&start_date=2015-01-01)


##### Parameter errors:
- [wrong freq](https://minikep-db.herokuapp.com/api/datapoints?name=ABC&freq=z&format=json)
- [wrong name for good freq](https://minikep-db.herokuapp.com/api/datapoints?name=ABC&freq=q&format=json)
- [start date in future](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2025-01-01)
- [end date > start date](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2015-01-01&end_date=2000-01-01)


#### GET ```info```:

Get a dictionary with variable description, allowed dates and latest values.

- [api/info?name=CPI_rog&freq=m](https://minikep-db.herokuapp.com/api/info?name=CPI_rog&freq=m)
- [api/info?name=GDP_yoy&freq=q](https://minikep-db.herokuapp.com/api/info?name=GDP_yoy&freq=q)
- [api/info?name=BRENT&freq=d](https://minikep-db.herokuapp.com/api/info?name=BRENT&freq=d)
- [api/info?name=USDRUR_CB&freq=d](https://minikep-db.herokuapp.com/api/info?name=USDRUR_CB&freq=d)

#### New methods

More methods [discussed here](https://github.com/mini-kep/db/issues/8#issuecomment-336152762).


#### POST ```api/datapoints``` 

Upsert data from json, as described in [intial spec](https://mini-kep.github.io/documentation/database/#post).

Requires API token.

#### DELETE ```api/datapoints``` 

Upsert data dased on 

Requires API token.


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
