from datetime import datetime
from sqlalchemy import desc
from db.api.models import Datapoint
from db.api.errors import CustomError400


def to_date(date_str: str):
    """Convert YYYY-MM-DD *date_str* to datetime.date object.
       Raises error if *date_str* not in YYYY-MM-DD format.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise CustomError400(f'Invalid date parameter {date_str}')


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
    if dicts:
        rows = list(yield_csv_row(dicts))
        return '\n'.join(rows)
    else:
        return ''


def validate_freq_exist(freq):
    possible_freq_values = Datapoint.query.group_by(Datapoint.freq) \
        .values(Datapoint.freq)
    # EP: redefining same variable is a bit questionable
    possible_freq_values = [row.freq for row in possible_freq_values]
    if freq not in possible_freq_values:
        msg = f'Invalid frequency <{freq}>'
        raise CustomError400(
            message=msg,
            payload={'allowed': possible_freq_values})


def validate_name_exist_for_given_freq(freq, name):
    possible_names_values = Datapoint.query.filter(Datapoint.freq == freq) \
        .group_by(Datapoint.name) \
        .values(Datapoint.name)
    # EP: redefining same variable is a bit questionable
    possible_names_values = [row.name for row in possible_names_values]
    if name not in possible_names_values:
        msg = f'No such name <{name}> for <{freq}> frequency.'
        raise CustomError400(message=msg,
                                    payload={"allowed": possible_names_values})


# EP: my wrong was to asks to shut this check, it is not a problem for custom API,
#     after a second thought
def validate_start_is_not_in_future(start_date):
    current_time = datetime.date(datetime.utcnow())
    if start_date >= current_time:
        raise CustomError400('Start date cannot be in the future')


def validate_end_date_after_start_date(start_date, end_date):
    if end_date < start_date:
        raise CustomError400('End date must be after start date')


def get_first_and_last_date(freq, name):
    # Extract first and last dates from datapoints with given freq, names
    start_date = Datapoint.query. \
        filter(Datapoint.name == name). \
        filter(Datapoint.freq == freq). \
        order_by(Datapoint.date). \
        first()
    start_date = datetime.strftime(start_date.date, "%Y-%m-%d")
    end_date = Datapoint.query. \
        filter(Datapoint.name == name). \
        filter(Datapoint.freq == freq). \
        order_by(desc(Datapoint.date)). \
        first()
    end_date = datetime.strftime(end_date.date, "%Y-%m-%d")
    return start_date, end_date


if __name__ == '__main__':
    from db import create_app
    from db.api.views import api as api_module

    # create test app
    app = create_app('config.DevelopmentConfig') 
    app.register_blueprint(api_module)
    
    # EP: works without db creation after done once
    # from db import db
    # db.create_all(app=create_app('config.DevelopmentConfig'))
    # db.init_app(app)
    #
    
    with app.app_context():
        possible_names_values = Datapoint.query.filter(Datapoint.freq == 'd') \
            .group_by(Datapoint.name) \
            .values(Datapoint.name)
        assert list(possible_names_values) == []

    
    # EP: without  with app.app_context() will prodcue error
    #
    # RuntimeError: No application found. Either work inside a view function or
    #               push an application context.>
    #
