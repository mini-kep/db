[![Build Status](https://travis-ci.org/mini-kep/db.svg?branch=flask_sqlalchemy)](https://travis-ci.org/mini-kep/db)

Can try GET method as:
- <https://minikep-db.herokuapp.com/api/datapoints?name=CPI_rog&freq=m>
- <https://minikep-db.herokuapp.com/api/datapoints?name=GDP_yoy&freq=q>
- <https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2017-01-01>
- <https://minikep-db.herokuapp.com/api/datapoints?name=USDRUR_CB&freq=d&start_date=2017-08-01&end_date=2017-10-01>

TODO:
- ```api/datapoints/varnames/{freq}``` lists all variable names available as that frequency ```{freq}``` (assumed to be in ```aqmwd```)
- variable descriptions ```GDP``` -> ```Gross domestic product```
- [varname splitter](https://github.com/mini-kep/parser-rosstat-kep/blob/master/src/csv2df/util_label.py) goes to helper function, will need to use it locally 
- use [unit descriptions](https://github.com/mini-kep/parser-rosstat-kep/blob/master/src/csv2df/specification.py#L74-L84)
