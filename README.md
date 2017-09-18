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

- 

## Changelog


- we rejected <https://flask-restless.readthedocs.io/en/stable/> blueprint
  as more specialised import is needed
  
- PonyORM fast-illustarted the project pipeline in <...>
  
- *pipeline.py* models whole dataflow across project, 
  moved to [parent repo](https://github.com/mini-kep/intro/blob/master/pipeline_demo.py)
