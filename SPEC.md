
Introduction 
============

```mini-kep``` is a small ETL (extract, transform, load) framework for macroeconomic data with public API for the database.
```mini-kep``` code enables a pipeline for data sources (static files in internet and public APIs) to own database to user API to 
get pandas dataframes. We want a user to be able to run:
```
pd.read_json("http://ourapp.com/ru/series/CPI/m/rog/2017")
```
to get mothly consumer inflation time series for Russia in 2017 or 
```
pd.read_json("http://ourapp.com/oil/series/BRENT/d/2000/2005") 
```
to get daily oil prices for Brent between 2000 and 2005.


Scope of this document
======================

This document descibes database layer, in the dta pipelineit is preceded by parsers and followed to end-user API:
```
parsers -> database -> user API
```

Some requirements:
- parser can deliver a list of dicts, each dict is a datapoint
- database should have a POST method to api\incoming to write incoming json to db
- POST operation shoudl have some authentication
- for simplicity all data is upserted - newer data overwrites older data
- database has GET method is styled around the datapoint key (variable name, frequency) and filtered by start date and end date
- GET operation is public API

Database schema
===============

Table **Datpoint**

Id – UID, autoincrement  
Name – type String \*  
Freq – type String \*  
Date – type DateTime \*  
Value – Float  

See example at <https://github.com/mini-kep/db/blob/master/demo/sqlalchemy/datapoint.py>

Methods
=======

2)	Available methods and descritpion of incoming/outgoing data


2.1)	GET / API/values with following URL parameters:
fromDate – should return results with date greater than this parameter.
toDate – should return results with date less than this parameter
Freq – freq value to search like freq=m
Name – name value to search like name=BRENT
fromValue - should return results with value greater than this parameter
toValue - should return results with value less than this parameter. <br>
Method returns JSON with data sorted by date or empty JSON if there’s no data with such query.
Method validates parameters and returns error 400 if there’s an error in parameters (like string in data parameter or empty parameter) <br>
2.2)	POST /API/incoming
Body should have a structure like
    [{
        "date": "1999-01-31",
        "freq": "m",
        "name": "INVESTMENT_rog",
        "value": 12345.6
    },
    {...} 
    ]
<br>Insert new data with values in request body.
All fields should be filled.
Method validates values, return error 400 if there’s an error in parameters (like string in data parameter or empty parameter or missing field)
Method returns empty JSON on success.<br>
3)	Tech stack:
Web-frameworks: Flask, Django + SQLAlchemy (deployed to Heroku)
Database: Postgres (Heroku or AWS)
Scheduler (for periodic database updates): [Heroku APS](https://devcenter.heroku.com/articles/clock-processes-python)
4)	Tests.
Upload data from JSON to DB, run python unit tests with requests to different methods, validate them with uploaded data.
Use combinations GET – POST – GET to validate data inserts and updates.
[Example1](https://github.com/mini-kep/db/blob/master/demo/sqlalchemy/tests/test_clientdb_demo.py)
[Example2](https://github.com/mini-kep/full-app/blob/master/datapoint/tests.py)
5)	Security.
POST methods should require API_TOKEN as URL parameter or header, validate it with environment variable (Heroku config vars)
