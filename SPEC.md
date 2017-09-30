Introduction 
============

```mini-kep``` is a small ETL (extract, transform, load) framework for macroeconomic data with public API for the database.

```mini-kep``` makes a pipeline from data sources (static files in internet and public APIs) to own database to user API to 
user's pandas dataframes. 

An end user may run: 
```python 

# get monthly consumer inflation time series for Russia in 2017
df = pd.read_json("http://ourapp.com/ru/series/CPI/m/rog/2017")

# get daily oil prices for Brent between 2000 and 2005
df = pd.read_json("http://ourapp.com/oil/series/BRENT/d/2000/2005") 

```

Scope of this document
======================

This document descibes database layer in between parsers and end-user API:

```
parsers -> database -> user API
```

Some requirements 
=================

- parser delivers a list of dicts, each dict is a datapoint
- database should have a POST method at ```api\incoming``` and write incoming json to db
- POST operation shoudl have some authentication
- for simplicity all data is upserted - newer data overwrites older data
- database has GET method is styled around the datapoint key (variable name, frequency), filtered by start date and end date, ordered by date 
- GET operation is public API
- there is another GET the is reponsible for calls like ```http://mini-db.herokuapp.com/oil/series/BRENT/d/2000/2005```

Database schema
===============

Table **Datpoint**
```
Id – UID, autoincrement  
Name – type String \*  eg GDP
Freq – type String \*  
Date – type DateTime \*  2016-12-31
Value – Float  

\* - composite key

```

See example at <https://github.com/mini-kep/db/blob/master/demo/sqlalchemy/datapoint.py>

Database methods
================

POST
----

```POST api/incoming``` 

Validates incoming json and upsert values to database. All fields should be filled.

Returns:
- empty JSON on success
- error 400 if there’s an error in incoming json (eg invalid date string or empty parameter or missing field)

#### Data structure - incoming json

Incoming json should have a structure like
    [{
        "date": "1999-03-31",
        "freq": "q",
        "name": "INVESTMENT_bln_rub",
        "value": 12345.6
    },
    {...} 
    ]

Parser result is obtained by  ```Dataset.yield_dicts(start='2017-01-01')``` in <https://github.com/mini-kep/parsers/blob/master/parsers/runner.py>, see ```Dataset.serialise()``` for json creation.

Other examples of incoming json:

- a large (1.8M) json is [located here](https://github.com/mini-kep/intro/blob/master/pipeline/dataset.json)
- sample data is presented [here](https://github.com/mini-kep/full-app/issues/9#issuecomment-331814995)

GET (REST)
----------

```GET api/datapoints```

2.1)	GET / API/values with following URL parameters:
fromDate – should return results with date greater than this parameter.
toDate – should return results with date less than this parameter
Freq – freq value to search like freq=m
Name – name value to search like name=BRENT
fromValue - should return results with value greater than this parameter
toValue - should return results with value less than this parameter. <br>
Method returns JSON with data sorted by date or empty JSON if there’s no data with such query.
Method validates parameters and returns error 400 if there’s an error in parameters (like string in data parameter or empty parameter) 

GET (Custom API)
----------------

Custom API allows call like mentioned in intro:

See <https://github.com/mini-kep/frontend-app/issues/8>

Interpretation 


Security
========

POST methods should require API_TOKEN as URL parameter or header, validate it with environment variable (Heroku config vars)

Tests
=====

Upload data from JSON to DB, run python unit tests with requests to different methods, validate them with uploaded data.
Use combinations GET – POST – GET to validate data inserts and updates.
[Example1](https://github.com/mini-kep/db/blob/master/demo/sqlalchemy/tests/test_clientdb_demo.py)
[Example2](https://github.com/mini-kep/full-app/blob/master/datapoint/tests.py)

Tech stack
==========

Web-frameworks: Flask, Django + SQLAlchemy (deployed to Heroku)
Database: Postgres (Heroku or AWS)
Scheduler (for periodic database updates): [Heroku APS](https://devcenter.heroku.com/articles/clock-processes-python)
