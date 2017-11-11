from datetime import datetime

from db.api.models import Datapoint
from db import db
from collections import OrderedDict

def to_date(date_str: str):
    """Convert YYYY-MM-DD *date_str* to datetime.date object.
       Raises error if *date_str* not in YYYY-MM-DD format.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f'Invalid date parameter {date_str}')


def date_as_str(dt):
    """Convert datetime.date object *dt* to YYYY-MM-DD string."""
    return datetime.strftime(dt, "%Y-%m-%d")


class Allowed(object):        
    def frequencies():
        return select_unique_frequencies()
        
    def names(freq):
        return possible_names_values(freq)


def _select_datapoints(freq: str, name: str, start_date, end_date):
    """Return dictionaries with datapoints, corresposding to *freq*, *name*
       and bounded by dates.
        
       Returns:   
           Iterable Query object <http://docs.sqlalchemy.org/en/latest/orm/query.html>
    """   
    data = Datapoint.query.filter_by(name=name, freq=freq)
    if start_date:
        data = data.filter(Datapoint.date >= start_date)
    if end_date:
        data = data.filter(Datapoint.date <= end_date)
    return data


def select_datapoints(**kwargs):
    """Return dictionaries with datapoints, corresposding to *freq*, *name*
       and bounded by dates.
        
       Returns:   
           Iterable Query object <http://docs.sqlalchemy.org/en/latest/orm/query.html>
    """   
    return _select_datapoints(**kwargs).order_by(Datapoint.date)


def select_dataframe(freq: str, names: list, start_date, end_date):
    # FIXME: edit docstring 
    """
    Returns dataframe corresponding to *freq*, *names* and bounded by dates
    dataframe is OrderedDict like
    (
        ('2017-11-05', [{
                  'name': *names[0]*,
                  'value': str(value of datapoint)
               },
               {
                  'name': *names[1]*,
                  'value': str(value of datapoint)
               } ...
               ]
        ...
    )
    Where keys are date strings
    And values are array with dicts that represends datapoints
    If there's no datapoint, 'value' would be an empty string
    """
    # FIXME: is this select dataframe code repeated?
    data = Datapoint.query.filter_by(freq=freq).filter(Datapoint.name.in_(names)).order_by(Datapoint.date)
    if start_date:
        data = data.filter(Datapoint.date >= start_date)
    if end_date:
        data = data.filter(Datapoint.date <= end_date)
    # -----------------------------------------------
    
    result = OrderedDict()
    # FIXME:
    # what does this comprehension mean? d[0] for d in data.values(Datapoint.date)
    for date in (date_as_str(d[0]) for d in data.values(Datapoint.date)):
        result[date] = []
        datapoints = data.filter_by(date=date)
        for name in names:
            dp = datapoints.filter_by(name=name).first()
            datapoint = {
                # FIXME: why we need 'name' here? are we double-checkingthe data structure later?     
                #        why this needs to be a dictionary?
                'name': name,
                'value': str(dp.value) if dp else ''
            }
            # FIXME: does this guarantee order is Ordereddict?
            result[date].append(datapoint)
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
    dt = Datapoint.query.filter_by(freq=freq, name=name) \
               .order_by(sorter) \
               .first()
    return date_as_str(dt.date)
     
          
class DateRange:
    def __init__(self, freq, name):
        self.freq, self.name = freq, name
        
    def get_boundary(self, direction):
        return get_boundary_date(self.freq, self.name, direction)
       
    @property    
    def min(self):
        return self.get_boundary(direction='start')

    @property    
    def max(self):
        return self.get_boundary(direction='end')    
               

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


# FIXME - delete fails

#def delete_datapoints(freq: str, name: str, start_date, end_date):
#    """Deletes datapoints with a specified arguments."""
#    data = _select_datapoints(freq, name, start_date, end_date)
#    data.delete()
#    db.session.commit()
#    

if __name__ == '__main__': # pragma: no cover
    from db import create_app
    from db.api.views import api 

    # create test app
    app = create_app('config.DevelopmentConfig') 
    app.register_blueprint(api)
    
    #EP: works without db creation after done once
    #from db import db
    #db.create_all(app=create_app('config.DevelopmentConfig'))

    with app.app_context():       
        dr = DateRange('a', 'GDP_yoy')
        print(dr.min)
                
        
    
    
