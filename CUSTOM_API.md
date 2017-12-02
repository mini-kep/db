<table>   
<tr>
    <td><b>Repository:</b></td>
    <td><a href="https://github.com/mini-kep/db/tree/master/db/custom_api">https://github.com/mini-kep/db/tree/master/db/custom_api</a>
    </td>
</tr>
</table>


# Overview

Custom API is a simplified interface for end-user database queries like:

- [oil/series/BRENT/m/eop/2015/2017/csv](http://minikep-db.herokuapp.com/oil/series/BRENT/m/eop/2015/2017/csv)
- [ru/series/EXPORT_GOODS/m/bln_usd](http://minikep-db.herokuapp.com/ru/series/EXPORT_GOODS/m/bln_usd)

Сustom API is intended for:

1. intuitive construction of URL by user
2. shorter notation than standard database API GET method 
3. addressing several database API endpoints in one place
4. uniform call to same indicator for different countries or regions

Its design originally discussed at [this issue](https://github.com/mini-kep/frontend-app/issues/8).

Custom API is essentially a thin syntax layer on top of database API. 
All calls to custom API are redirected to standard API. For example, these calls to custom and standard APIs will return same data:  

- <http://minikep-db.herokuapp.com/ru/series/CPI/m/rog/2015/2017>
- <http://minikep-db.herokuapp.com/api/datapoints?name=CPI_rog&freq=m&start_date=2015-01-01&end_date=2017-12-31>

   
URL syntax
==========

```
URL format (? marks optional parameter):

    {domain}/series/{varname}/{freq}/{?suffix}/{?start}/{?end}/{?finaliser}
    
Args:    
    {domain} is reserved, future use: 'all', 'ru', 'oil', 'us', 'ru:bank', 'ru:77'
	
    {varname} is GDP, GOODS_EXPORT, BRENT (capital letters with underscores)
	
    {freq} is any of:
         a (annual)
         q (quarterly)
         m (monthly)
         w (weekly)
         d (daily)
	 
    {?start} or {?end} are years
	
    {?suffix} may be:
	
    unit of measurement ('unit'):
        example: bln_rub, bln_usd, tkm (lowercase with underscores)
	
    rate of change for real variable ('rate'):
	rog - change to previous period
	yoy - change to year ago
	base - base index
	
    aggregation command ('agg'):
	eop - end of period
	avg - average
   
    {?finaliser}:
        csv - comma-delimited file
        json - list datapoints in JSON format       
        xlsx - Excel (xlsx) file  
        info - show variable info, not data 		
		
```

Refer to the docstring in 
[custom_api.py](https://github.com/mini-kep/helper-custom-api/blob/master/src/custom_api.py) 
for details 

Expected usage of ```{domain}``` is to get similar data 
for different countries or regions by changing a little part of custom URL:

```
   ru/series/CPI/m/2017  # country-level inflation for Russia 
ru:77/series/CPI/m/2017  # inflation for Moscow region                         
   kz/series/CPI/m/2017  # country-level inflation for Kazakhstan
```

# Output format

By default custom API returns CSV file. This file is:

- viewable in browser (download does not start)
- readable by R/pandas

Optional  ```{finaliser}``` may alter output format.


# Examples

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
