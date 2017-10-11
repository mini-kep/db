from datetime import datetime
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
        return '<br>'.join(rows)
    else:
        return ''
