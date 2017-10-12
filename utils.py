from datetime import datetime
from db.api.models import Datapoint
from db.api.errors import Custom_error_code_400


# Convert YYYY-MM-DD string to datetime.date object.
def to_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise Custom_error_code_400(f'Invalid date parameter {date_str}')


# serialiser fucntion
def yield_csv_row(dicts):
    """
    Arg:
       dicts - list of dictionaries like
               {'date': '1992-07-01', 'freq': 'd', 'name': 'USDRUR_CB', 'value': 0.1253}

    Returns:
       string like ',USDRUR_CB\n1992-07-01,0.1253\n'
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
    possible_freq_values = Datapoint.query.group_by(Datapoint.freq).values(Datapoint.freq)
    possible_freq_values = [row.freq for row in possible_freq_values]
    if freq not in possible_freq_values:
        raise Custom_error_code_400(message=f'Invalid value for parameter \'freq\', check possible values list in \'allowed\'',
                                    payload={'allowed':possible_freq_values})


def validate_name_exist_for_given_freq(freq, name):
    possible_names_values = Datapoint.query.filter(Datapoint.freq==freq).group_by(Datapoint.name).values(Datapoint.name)
    possible_names_values = [row.name for row in possible_names_values]
    if name not in possible_names_values:
        raise Custom_error_code_400(message=f'Invalid value for parameter \'name\', '
                                    f'check possible values list for freq \'{freq}\' in \'allowed\'',
                                    payload={"allowed":possible_names_values})


def validate_and_convert_dates(start_date, end_date):
    if start_date:
        start_date = to_date(start_date)
        # https://github.com/mini-kep/db/issues/13   lets drop this check, it is a bit too restrictive
        #current_time = datetime.date(datetime.utcnow())
        #if start_date >= current_time:
        #    raise Custom_error_code_400('Start date can\'t be more than current date')
    if end_date:
        end_date = to_date(end_date)
        if start_date and end_date < start_date:
            raise Custom_error_code_400('End date can\'t be more than start date')
    return start_date, end_date
