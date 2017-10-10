from datetime import datetime


# Convert YYYY-MM-DD string to datetime.date object.
def to_date(date_str: str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


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
