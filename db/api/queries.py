from datetime import datetime

from db.api.models import Datapoint
from db import db
from collections import OrderedDict

# TODO: duplicate of utilf fucntion
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


class DatapointOperations:  
    
    @staticmethod
    def _base_select(freq: str, start_date, end_date):
        data = Datapoint.query.order_by(Datapoint.date)
        if freq:
            data = data.filter_by(freq=freq)
        if start_date:
            data = data.filter(Datapoint.date >= start_date)
        if end_date:
            data = data.filter(Datapoint.date <= end_date)
        return data

    def select(freq: str, name: str, start_date, end_date):
        """Return dictionaries with datapoints, corresposding to 
           *freq*, *name* and *start_date* and *end_date*.
           
           Can search just by few arguments, the rest can be None or False. 
           Example:
               select_datapoints('a', None, None, None)
            
           Returns:   
               Iterable Query object <http://docs.sqlalchemy.org/en/latest/orm/query.html>
        """
        data = DatapointOperations._base_select(freq, start_date, end_date)
        if name: 
            data = data.filter_by(name=name)
        return data

    def select_frame(freq: str, names: list, start_date, end_date):
        data = DatapointOperations._base_select(freq, start_date, end_date)
        if names: 
            data = data.filter(Datapoint.name.in_(names))
        return data
    
    
    def upsert(datapoint):
        """Inserts *datapoint* dictionary into the DB if not present, updates its value otherwise.
           Datapoint's unique constraint on ("name", "freq", "date") columns guarantees
           there might be only one row found, therefore it is safe to retrieve a single
           datapoint using .first()
        """
        existing_datapoint = Datapoint.query \
            .filter(Datapoint.freq == datapoint['freq']) \
            .filter(Datapoint.name == datapoint['name']) \
            .filter(Datapoint.date == datapoint['date']) \
            .first()
        if existing_datapoint:
            existing_datapoint.value = datapoint['value']
        else:
            db.session.add(Datapoint(**datapoint))
    
    
    def delete(freq: str, name: str, start_date, end_date):
        """Delete datapoints with specified arguments. 
           Arguments is the same as in *select_datapoints()*.
        """
        query = DatapointOperations.select(freq, name, start_date, end_date)
        # WONTFIX: may check length query.count() and raise error if nothing to delete
        for item in query:
            db.session.delete(item)
        db.session.commit()


   
class All:
    def frequencies():
        return select_unique_frequencies()
        
    def names():
        return name_values(freq=None)

class Allowed(object):        
    def frequencies(name):
        return select_unique_frequencies(name)
        
    def names(freq):
        return name_values(freq)


def select_unique_frequencies(name=None):
    """Return a list of allowed frequencies.
       Returns:
           list of strings, likely a subset of ['a', 'q', 'm', 'w', 'd'].
    """
    query = Datapoint.query
    if name:
        query = query.filter_by(name=name)
    query = query.group_by(Datapoint.freq) \
                 .order_by(Datapoint.freq) \
                 .values(Datapoint.freq)
                 # the query result will be undefined without .values(...)
                 # it passes on sqlite, but fails on postgres                 
    return [row.freq for row in query]


def name_values(freq=None):
    """Return a list of variable names corresponding to frequency *freq*.
       Args:
           freq(str) - one letter from 'aqmwd' or None
       Returns:
           list of strings
    """
    query = Datapoint.query
    if freq:
        query = query.filter_by(freq=freq)
    query = query.group_by(Datapoint.name) \
                 .order_by(Datapoint.name) \
                 .values(Datapoint.name)
                 # the query result will be undefined without .values(...)
                 # it passes on sqlite, but fails on postgres
    return [row.name for row in query]


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


# 'pragma: no cover' exludes code block from coverage
if __name__ == '__main__': # pragma: no cover
    from db import create_app
    from db.api.views import api 

    # create test app
    app = create_app('config.DevelopmentConfig') 
    app.register_blueprint(api)
    
    #EP: works without db creation after done once
    db.create_all(app=create_app('config.DevelopmentConfig'))

    with app.app_context():       
        dr = DateRange('q', 'GDP_yoy')
        print(dr.min)
        #delete_datapoints("a", None, None, None)
        q = DatapointOperations.select(freq = 'd', 
                              name = None,
                              start_date = None, 
                              end_date = None) 
        print(q.count())
        
        from datetime import date
        param = dict(freq='m',
                     name='CPI_ALCOHOL_rog',
                     start_date= date(year=2016, month=6, day=1),
                     end_date= date(year=2016, month=7, day=1))
        q3 = DatapointOperations.select(**param)
        
        # TODO: make test + approve + parametrise it
        assert ['a', 'q'] == Allowed.frequencies('GDP_yoy')
        assert ['d'] == Allowed.frequencies('BRENT')
        
        do = DatapointOperations.select(None, None, None, None)
        
        freqs = select_unique_frequencies(None)
        assert freqs ==  ['a', 'd', 'm', 'q']
    