"""Helpers:

    - date functions
    - serialisers

"""
from datetime import datetime
from db.api.models import Datapoint
from db.api.errors import CustomError400
import db.api.queries as queries


def to_date(date_str: str):
    """Convert YYYY-MM-DD *date_str* to datetime.date object.
       Raises error if *date_str* not in YYYY-MM-DD format.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise CustomError400(f'Invalid date parameter {date_str}')
#
#def date_as_str(dt):
#    """Convert datetime.date object *dt* to YYYY-MM-DD string."""
#    return datetime.strftime(dt.date, "%Y-%m-%d")

def yield_csv_row(dicts):
    """Serialiser function to create CSV rows as strings.

    Arg:
       dicts - list of dictionaries like
               {'date': '1992-07-01', 'freq': 'd',
                'name': 'USDRUR_CB', 'value': 0.1253}

    Yeilds:
        csv header like ',USDRUR_CB'
        followed by rows like '1992-07-01,0.1253'
        followed by empty string at end
    """
    datapoints = list(dicts)
    name = datapoints[0]['name']
    yield ',{}'.format(name)
    for d in datapoints:
        yield '{},{}'.format(d['date'], d['value'])
    # this yield is responsible for last \n in csv
    yield ''


def to_csv(dicts):
    """Wrapper for yield_csv_row()"""
    if dicts:
        rows = list(yield_csv_row(dicts))
        return '\n'.join(rows)
    else:
        return ''

# FIXME: 
#       - rename to yield_csv_dataframe_rows, because yeilding one row is only this yield '{},{}'.format(date, ','.join(values))
#         OR split into two funcs and use them in dataframe_to_csv()
#       - document what datatipe dataframe is? pandas dataframe? dictionary? 
#       - provide dataframe argument example is docstring  
def yield_csv_dataframe_row(dataframe, names):
    yield ',{}'.format(','.join(names))
    # FIXME: names could be used here as well to guarantee order. order is not guaranteed now, responsibility outside function 
    for date, datapoints in dataframe.items():
        values = [dp['value'] for dp in datapoints]
        yield '{},{}'.format(date, ','.join(values))
    yield ''


def dataframe_to_csv(dataframe, names):
    if dataframe:
        # FIXME: option: can contruct from csv header and csv body here  
        rows = list(yield_csv_dataframe_row(dataframe, names))
        return '\n'.join(rows)
    else:
        return ''


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
        z = [d.value for d in Datapoint.query.filter(Datapoint.freq == 'd').all()]
        query = Datapoint.query.filter(Datapoint.freq == 'd') \
                               .group_by(Datapoint.name) \
                               .values(Datapoint.name)
        k = [x.name for x in query]    
        assert k == ['BRENT', 'USDRUR_CB']
        assert set(['a', 'd', 'm', 'q']) == \
               set(queries.select_unique_frequencies())
        
