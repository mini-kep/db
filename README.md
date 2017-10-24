[![Build Status](https://travis-ci.org/mini-kep/db.svg?branch=master)](https://travis-ci.org/mini-kep/db)
[![Assertible status](https://assertible.com/apis/56e34b07-ae3a-4248-937e-fef69d8ec2f2/status?api_token=VkiQoHOdjWU3vGv2)](https://assertible.com/dashboard#/services/56e34b07-ae3a-4248-937e-fef69d8ec2f2/results)
[![Coverage badge](https://codecov.io/gh/mini-kep/db/branch/master/graphs/badge.svg)](https://codecov.io/gh/mini-kep/db)

# Quickstart

At ```api/datapoints``` you can query macroeconomic database by indicator name, frequency and date range. 

For example, [this link](https://minikep-db.herokuapp.com/api/datapoints?name=GDP_yoy&freq=q&start_date=2016-01-01) 
will provide quarterly year-on-year GDP growth rates as csv file, readable by R/pandas:

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

# Standard API 

Standard API is REST-like interface to upload/retrieve time-series data. 
Brief initial specification for it is [here](https://mini-kep.github.io/documentation/database/),
updates are documented below.

## ```datapoints``` POST method

Upsert data from json, as described in [intial spec](https://mini-kep.github.io/documentation/database/#post).

## GET methods 

#### ```names```:
- [api/names/a](https://minikep-db.herokuapp.com/api/names/a)
- [api/names/q](https://minikep-db.herokuapp.com/api/names/q)
- [api/names/m](https://minikep-db.herokuapp.com/api/names/m)
- [api/names/d](https://minikep-db.herokuapp.com/api/names/d)

#### ```datapoints```:
- [api/datapoints?name=CPI_rog&freq=m](https://minikep-db.herokuapp.com/api/datapoints?name=CPI_rog&freq=m)
- [api/datapoints?name=GDP_yoy&freq=q](https://minikep-db.herokuapp.com/api/datapoints?name=GDP_yoy&freq=q)
- [api/datapoints?name=BRENT&freq=d&start_date=2017-01-01](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2017-01-01)
- [api/datapoints?name=USDRUR_CB&freq=d&start_date=2017-08-01&end_date=2017-10-01](https://minikep-db.herokuapp.com/api/datapoints?name=USDRUR_CB&freq=d&start_date=2017-08-01&end_date=2017-10-01)

##### Parameter errors:
- [wrong freq](https://minikep-db.herokuapp.com/api/datapoints?name=ABC&freq=z&format=json)
- [wrong name for good freq](https://minikep-db.herokuapp.com/api/datapoints?name=ABC&freq=q&format=json)
- [start date in future](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2025-01-01)
- [end date > start date](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2015-01-01&end_date=2000-01-01)


#### ```info```:
- [api/info?name=CPI_rog&freq=m](https://minikep-db.herokuapp.com/api/info?name=CPI_rog&freq=m)
- [api/info?name=GDP_yoy&freq=q](https://minikep-db.herokuapp.com/api/info?name=GDP_yoy&freq=q)
- [api/info?name=BRENT&freq=d](https://minikep-db.herokuapp.com/api/info?name=BRENT&freq=d)
- [api/info?name=USDRUR_CB&freq=d](https://minikep-db.herokuapp.com/api/info?name=USDRUR_CB&freq=d)

#### new methods

More methods [discussed here](https://github.com/mini-kep/db/issues/8#issuecomment-336152762).


# Custom API

Provides more user-friendly syntax for ```GET \api\datapoints```. 

Breif overview [here](https://mini-kep.github.io/documentation/custom_api/) and
latest comments in [custom_api.py docstring](https://github.com/mini-kep/db/blob/master/db/custom_api/custom_api.py#L1)

#### Example calls
- basic calls:
  - [/ru/series/GDP/a/yoy/1998/2017](http://mini-kep.herokuapp.com/ru/series/GDP/a/yoy/1998/2017)
- units:
  - [ru/series/CPI_rog/m/2000/2010)](http://mini-kep.herokuapp.com/ru/series/CPI_rog/m/2000/2010)
  - [ru/series/CPI/m/rog/2000/2010](http://mini-kep.herokuapp.com/ru/series/CPI/m/rog/2000/2010)
- other:
- [/ru/series/CPI_ALCOHOL/m/2016/rog](https://minikep-db.herokuapp.com/ru/series/CPI_ALCOHOL/m/2016/rog)
- [/ru/series/USDRUR_CB/d/2000/2001](https://minikep-db.herokuapp.com/ru/series/USDRUR_CB/d/2015/2016)
- [/oil/series/BRENT/d/2017](https://minikep-db.herokuapp.com/oil/series/BRENT/d/2017)

#### Sample user code

```python
import pandas as pd

def read_ts(source_url):
	"""Read pandas time series from *source_url*."""
	return pd.read_csv(source_url, 
                      converters={0: pd.to_datetime}, 
                      index_col=0,
                      squeeze=True)

er = read_ts('http://mini-kep.herokuapp.com/ru/series/USDRUR_CB/d/2017/')

assert er['2017-09-28'] == 58.01022

```

