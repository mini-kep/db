"""Scripts below make use of GET methods of API that delivers macroeconomic time series.

Testing is done on an actual URL: <https://minikep-db.herokuapp.com/>

Call examples:
- https://minikep-db.herokuapp.com/api/datapoints?name=GDP_yoy&freq=q&start_date=2016-01-01
- https://minikep-db.herokuapp.com/api/names/d
- https://minikep-db.herokuapp.com/api/info?name=GDP_yoy&freq=q

API documentation:
- <https://github.com/mini-kep/db/blob/master/README.md>

Checklist with some ideas:
- <http://python.apichecklist.com/>

<access.py> and <minikep.py> provide wrappers for the API,
one file uses functions and another one is based on classes.
<access.py> is good to embed in ipython notebooks.

This file needs fixes/engancements in FIXME and TODO parts +
can be converted to randomised test or integration test,
querieng all of the database.

Note here we test GET methods only, not POST or DELETE.

"""

import random
import access


#  'api/freq' returns {'a', 'q', 'm', 'd'} frequencies
frequencies = ['a', 'q', 'm', 'd']
assert set(access.get_freq()) == set(frequencies)

# 'api/names'
freq = random.choice(frequencies)
names = access.get_names(freq)
name = random.choice(names)
assert isinstance(name, str)
assert name[0].isupper()

# 'api/info'
info = access.get_info(freq, name)

start_date = info['start_date']
latest_date = info['latest_date']

assert parse(start_date).date().isoformat() == start_date
assert parse(latest_date).date().isoformat() == latest_date

assert access.get_unit_id(name) == info['unit_id']
assert access.get_var_id(name) == info['var_id']
start_date = info[freq]['start_date']
latest_date = info[freq]['latest_date']
# WONTFIX: access.get_info(freq, name) should retrun a more flat data structure
# TODO: check start_date and latest_date are ISO dates
# TODO: more checks for info

# 'api/datapoints'
params = dict(
    freq=freq,
    name=name,
    start_date=start_date,
    end_date=latest_date)
ts = access.get_ts(**params)
# FIXME: any cheks here?

#  'api/frame'
freq = 'a'
names = access.get_names(freq)
df1 = access.get_frame(freq)

# frame has same variables as names
assert all(df1.keys() == names)

# frame is identical to composition of time series
# FIXME: must also check on shorter dates or other frequencies
#        + check on time series with missing values
series_list = [access.get_ts(freq=freq, name=name) for name in names]
df2 = access.join_df([ts.to_frame() for ts in series_list])
assert all(df1 == df2)

# pick 3 random names
random_names = [random.choice(names) for i in range(1, 3)]

#  get result from api/datapoints, concat ts
series_list = [MiniKEP.datapoints_csv(freq=freq, name=name).to_frame() for name in random_names]

df1 = access.join_df([ts.to_frame() for ts in series_list])

# get frame
df2 = MiniKEP.frame(freq=freq, names=random_names)

# compare
assert all(df1 == df2)
    
=======
# TODO: pick 3 random names from names, get result from api/frame,
#       get result from api/datapoints, concat ts, compare.
#       can use access2.py for this


# custom api
param = dict(freq='m', name='CPI_rog',
             start_date='2015-01-01', end_date='2017-12-31')
standard_api_ts = access.get_ts(**param)
param2 = dict(freq='m', name='CPI', suffix='rog',
              start='2015', end='2017')
custom_api_ts = access.get_custom_series(**param2)
assert all(custom_api_ts == standard_api_ts)
