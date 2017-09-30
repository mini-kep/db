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

This document describes database layer in between parsers and end-user API:

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

For insert_ьфтн щзукфешщт see sheep/flock example at <https://stackoverflow.com/a/33768160/1758363>

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

```GET api/datapoints?name=<name>&freq=<freq>```
```GET api/datapoints?name=<name>&freq=<freq>&start_date=<start_date>&end_date=<end_date>```

Parameters:
name – name value to search like name=BRENT
freq – freq value to search like freq=m
start_date(optional) – should return results with date greater than this parameter
end_date(optional) – should return results with date less than this parameter

Returns:
- JSON in format similar to incoming json with data sorted by date
- empty JSON if there’s no data with such query.

Method validates parameters and returns error 400 if there’s an error in parameters (like string in data parameter or empty parameter) 

GET (Custom API) 
----------------

Custom API allows call like mentioned in intro. See <https://github.com/mini-kep/frontend-app/issues/8>

Custom API will be implemented outside of db layer. 

Security
========

POST methods should require API_TOKEN as URL parameter or header, validate it with environment variable (possibly Heroku config vars)

Tests
=====

Upload data from JSON to DB, run python unit tests with requests to different methods, validate them with uploaded data.
Use combinations GET – POST – GET to validate data inserts and updates.
[Example1](https://github.com/mini-kep/db/blob/master/demo/sqlalchemy/tests/test_clientdb_demo.py)
[Example2](https://github.com/mini-kep/full-app/blob/master/datapoint/tests.py)

Should we write some tests in curl/httpie? 

Tech stack
==========
To discuss:

Web-frameworks: Flask + SQLAlchemy or Django, may consider Falcon

Rest frameworks: 
- flask: <https://github.com/flask-restful/flask-restfuls>
- django: <http://www.django-rest-framework.org/>

Container: prototype can be deployed to Heroku, for production it is rather expensive, may need to use  AWS

Database: Postgres (default on Heroku) or other on AWS


Additions
=========
Outisde of scope of current implementation:
- GET (Custom API) 
- scheduler (for periodic database updates): [Heroku APS](https://devcenter.heroku.com/articles/clock-processes-python)
