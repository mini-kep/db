# db
Database blueprint to store macroeconomic datapoints

## Objective:

 - we want a flask app with database inside that has methods to store 
   and retrieve data
   
 - our data is now a json/dict like 
   ```dict(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)``` or 
   a list of such dicts.
   

## TODOs
- now: slqa table with tested CRUD methods
- next: interfaces to accept json / return json as in pipeline 
- after: integrate with parsers / frontend app

   
## Current focus:  

<https://github.com/mini-kep/db/blob/master/clientdb.py> and its testing

## Changelog

- <https://github.com/mini-kep/db/blob/master/tests/test_sqla_demo.py> tests
  abandoned in favour of <https://github.com/mini-kep/db/blob/master/clientdb.py>
  
  > test_sqla_demo.py makes little distinction between test setup, method tested
  > and result comparision - no suprise, we did not have access methods yet!
  > test_sqla_demo.py will be replaced/archived. 

- we rejected <https://flask-restless.readthedocs.io/en/stable/> blueprint
  as more specialised import is needed
  
- PonyORM used to fast-illustarte project pipeline in <https://github.com/mini-kep/db/blob/master/pony_demo/pony_demo.py>
  
- [pipeline.py](https://github.com/mini-kep/intro/blob/master/pipeline_demo.py)
  models whole dataflow across project