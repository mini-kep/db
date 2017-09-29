1)	Database schema:
Id – UID, autoincrement
Date – type DateTime
Freq – type String
Name – type String
Value – Float
[Example](https://github.com/mini-kep/db/blob/master/demo/sqlalchemy/datapoint.py)

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
