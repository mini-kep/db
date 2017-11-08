from db.api.models import Datapoint
from db import db
import datetime

def select_datapoints(freq: str, name: str, start_date, end_date):
    """Return dictionaries with datapoints, corresposding to *freq*, *name*
        and bounded by dates.
        
        Returns:   
           Query object <http://docs.sqlalchemy.org/en/latest/orm/query.html>
           It is iterable. 
    """   
    data = Datapoint.query.filter_by(name=name, freq=freq).order_by(Datapoint.date)
    if start_date:
        data = data.filter(Datapoint.date >= start_date)
    if end_date:
        data = data.filter(Datapoint.date <= end_date)
    return data


def select_dataframe(freq: str, names: list, start_date, end_date):
    """
    Returns dataframe corresponding to *freq*, *names* and bounded by dates
    dataframe is dict like
    {
        date0: [{
                  'freq': *freq*,
                  'name': *names[0]*,
                  'date': *date0*
                  'value': value of datapoint
               },
               {
                  'freq': *freq*,
                  'name': *names[1]*,
                  'date': *date0*,
                  'value': value of datapoint
               } ...
               ]
        ...
    }
    Where keys are date strings
    And values are array with dicts that represends datapoints (or empty dict if there's no datapoint)

    """
    data = Datapoint.query.filter_by(freq=freq).filter(Datapoint.name.in_(names)).order_by(Datapoint.date)
    if start_date:
        data = data.filter(Datapoint.date >= start_date)
    if end_date:
        data = data.filter(Datapoint.date <= end_date)
    result = {}
    for date in (d[0] for d in data.values(Datapoint.date)):
        date_str = datetime.datetime.strftime(date, "%Y-%m-%d")
        result[date_str] = []
        datapoints = data.filter_by(date=date)
        for name in names:
            dp = datapoints.filter_by(name=name).first()
            result[date_str].append(dp.serialized if dp else {})
    return result


def select_unique_frequencies():
    """Return a list of allowed frequencies.    
       Returns:   
           list of strings, likely ['a', 'q', 'm', 'w', 'd'].
    """
    query = Datapoint.query.group_by(Datapoint.freq) \
                           .values(Datapoint.freq)
    return [row.freq for row in query]


def possible_names_values(freq):
    """Return a list of variable names corresponding to frequency *freq*.    
       Args:
           freq(str) - one letter from 'aqmwd' or 'all', not checked          
       Returns:   
           list of strings
    """
    query = Datapoint.query
    if freq != 'all':
        query = query.filter_by(freq=freq)
    query = query.group_by(Datapoint.name).\
                  order_by(Datapoint.name).\
                  values(Datapoint.name)
    return [row.name for row in query] 


def get_boundary_date(freq, name, direction):
    """Get first or last date for timeseries  *freq*, *name*.    
       Returns:
           SQLA own date object (?)
    """
    sorter = dict(start=Datapoint.date,
                  end=Datapoint.date.desc())[direction]
    return Datapoint.query.filter_by(freq=freq, name=name) \
               .order_by(sorter) \
               .first()


def upsert(datapoint):
    """Inserts *datapoint* dictionary into the DB if not present, updates its value otherwise.
       Datapoint's unique constraint on ("name", "freq", "date") columns guarantees
       there might be only one row found, therefore it is safe to retrieve a single
       datapoint using .first()
    """
    existing_datapoint = Datapoint.query. \
        filter(Datapoint.freq == datapoint['freq']). \
        filter(Datapoint.name == datapoint['name']). \
        filter(Datapoint.date == datapoint['date']). \
        first()

    if existing_datapoint:
        existing_datapoint.value = datapoint['value']
    else:
        db.session.add(Datapoint(**datapoint))
