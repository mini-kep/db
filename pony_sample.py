# -*- coding: utf-8 -*-
"""Prototype for central database in PonyORM."""

from pony import orm

db = orm.Database()
db.bind(provider='sqlite', filename=':memory:')

class Datapoint(db.Entity):
     freq = orm.Required(str)
     name = orm.Required(str)     
     date = orm.Required(str)
     value = orm.Required(float)  
     # TODO: make unique key freq, name, date
        
     
db.generate_mapping(create_tables=True)

orm.sql_debug(True)
# end of boilerplate

# 0. Example setup 
# this is to minic state of database before parser import 

with orm.db_session:
     x = Datapoint(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
     # this datapoint will overlap:
     x = Datapoint(date="2017-03-16", freq='d', name="BRENT", value=50.56)
     # later: things get worse when value is not 50.56 (a revision)

# 1. Import data from parser
# --------------------------

def mock_parser_output_2():   

    brent = [("2017-03-16", 50.56),
             ("2017-03-17", 50.58),
             ("2017-03-20", 50.67)]   
    
    for date, value in brent:
        yield {"date": date,
               "freq": "d",
               "name": "BRENT",
               "value": value}
    

def mock_parser_output_1():   
    
    yield {"date": "2015-11-30",
        "freq": "m",
        "name": "CPI_rog",
        "value": 100.8}
    
    yield {"date": "2015-11-30",
        "freq": "m",
        "name": "RUR_EUR_eop",
        "value": 70.39}
    
    yield {"date": "2015-12-31",
        "freq": "m",
        "name": "CPI_rog",
        "value": 100.8}
    
    yield {"date": "2015-12-31",
        "freq": "m",
        "name": "RUR_EUR_eop",
        "value": 79.7}
    
# put parcer data inside the database
with orm.db_session:
    for mock_output in [mock_parser_output_1, mock_parser_output_2]: 
        for x in mock_output():
            dp = Datapoint(**x)
        

# 2. Query database
# -----------------

 
user_query = dict(varnames=['CPI_rog', 'RUR_EUR_eop'],  freq='m')

# TODO: make json, readable by pandas.read_json()

import pandas as pd

# Pseudocode:
    
# TODO: make filter for select() based on user_query 
# TODO: get records

# make dataframe from records, similar to src.csv2df.emitter: 
df = pd.DataFrame([{"date": "2015-12-31",
"freq": "m",
"name": "CPI_rog",
"value": 100.8},
{"date": "2015-12-31",
"freq": "m",
"name": "RUR_EUR_eop",
"value": 79.7}])
df.date = pd.to_datetime(df.date)        
df = df.pivot(columns='name', values='value', index='date')

df_json = df.to_json()
user_df = pd.read_json(df_json)

# user_df.to_dict('list')
# Out[49]: {'CPI_rog': [100.8], 'RUR_EUR_eop': [79.7]}


# After 
# -----
# Screen what is inside the database

with orm.db_session:    
    res = orm.select((p.name, p.freq, p.date, p.value) for p in Datapoint)[:]
    
pprint(res)
    
