# -*- coding: utf-8 -*-

# see pony_demo and pipeline.py for scetches


# the job

"""
Main: make time series from different sources available to user to read as pd.DataFrame
Extras:
1. browse what data is available
2. convenient, clear address for the data
"""

# the design

# objects

"""
naming convention 
- common principles across project about variable names:  VAR_NAME_unit

data source 
- static files, eg <http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391>
- API, eg 

parser (mini-kep and others)
- downloads/reads source
- assigns varnames 
- output is controlled by history depth (all available datapoints or after specified date) 
- saves or returns standard **parser output**:
  - json with datapoint dictionaries 
  - same template for all parsers
  - parser name in json? or in each datapoint?

import controller (not repo yet, not cleat how to implement)
- 1. run the parser  
  - see what is missing in the database at a point in time
  - start/query the parser with requred depth
  - some jobs may be scheduled with cron-like 
- 2. upload to database
  - insert parser output to database
  - resolve conflicts (upsert as delete + insert)

database (mini-kep-db)
- single table for datapoints in a relational database with SQLAlchemy Core ORM layer 
- no other tables in database at start
- RUD funtionality via REST commands
- very generic component - may use template https://flask-restless.readthedocs.io/en/stable/

user app (mini-kep-app)  
- mix of html display and custom end-user API interface
- converts db output to pandas-readable json or csv (this can be on database side)

user queries
- something to test from
"""

# pseudocode and sample data structures

# better be a class?
def get_parser_result(parser_param):
    pass

# database PUT method
def to_database(datapoints):
    pass

# database GET method
def from_database(query_dict):
    pass

def as_user_json(result_dict):
    pass

# write into database
parser_param_1 = dict()
parser_result_1 = get_parser_result(parser_param_1)
to_database(parser_result_1)

# read from database
user_query = dict()
reponse = as_user_json(from_database(user_query))


class Datapoint(db.Entity):
     freq = orm.Required(str)
     name = orm.Required(str)     
     date = orm.Required(str)
     value = orm.Required(float)  
     # TODO: make unique key freq, name, date 
     # orm.PrimaryKey(freq, name, date)
     
