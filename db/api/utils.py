"""Helpers:

    - date functions
    - serialisers

"""
from datetime import datetime
from db.api.errors import CustomError400
import db.api.queries as queries


def date_as_str(dt):
    """Convert datetime.date object *dt* to YYYY-MM-DD string."""
    return datetime.strftime(dt, "%Y-%m-%d")


def to_date(date_str: str):
    """Convert YYYY-MM-DD *date_str* to datetime.date object.
       Raises error if *date_str* not in YYYY-MM-DD format.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise CustomError400(f'Invalid date parameter {date_str}')
#
# def date_as_str(dt):
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


def unique(seq):
    return sorted(list(set(seq)))


def serialiser(datapoint_query):
    dicts = [d.serialized for d in datapoint_query]
    dates = unique([x['name'] for x in dicts])
    result = dict()
    for dt in dates:
        this_date = {x['name']: x['value'] for x in dicts if x['date'] == dt}
        result[dt] = this_date
    return result


class DictionaryRepresentation:
    def __init__(self, datapoint_query):
        self.source_dict = [d.serialized for d in datapoint_query]
        self.names = unique([x['name'] for x in self.source_dict])
        self.dates = unique([x['date'] for x in self.source_dict])

    @property
    def dicts(self):
        result = dict()
        for dt in self.dates:
            this_date = {x['name']: x['value']
                         for x in self.source_dict if x['date'] == dt}
            result[dt] = this_date
        return result

    @property
    def header(self):
        return ',{}'.format(','.join(self.names))

    def yield_data_rows(self):
        for dt in self.dates:
            row = [dt]
            for name in self.names:
                try:
                    x = self.dicts[dt][name]
                except KeyError:
                    x = ''
                finally:
                    row.append(x)
            yield row

    def yield_rows(self):
        yield self.header
        for row in self.yield_data_rows():
            yield ','.join(map(str, row))
        yield ''

    def to_csv(self):
        return '\n'.join(self.yield_rows())


if __name__ == '__main__':  # pragma: no cover
    from db import create_app
    from db.api.views import api

    # create test app
    app = create_app('config.DevelopmentConfig')
    app.register_blueprint(api)

    # EP: works without db creation after done once
    #from db import db
    # db.create_all(app=create_app('config.DevelopmentConfig'))

    with app.app_context():

        # TODO: convert to test
        names = ['CPI_rog', 'EXPORT_GOODS_bln_usd']
        sample_query = queries.DatapointOperations.select_frame(
            'q', names, None, None)
        m = DictionaryRepresentation(sample_query)
        assert m.header == ',CPI_rog,EXPORT_GOODS_bln_usd'
        rows = m.yield_data_rows()
        next(rows) == ['2016-06-30', 101.2, 67.9]
        next(rows) == ['2016-09-30', 100.7, 70.9]
        next(rows) == ['2016-12-31', 101.3, 82.6]

        assert m.to_csv() == """,CPI_rog,EXPORT_GOODS_bln_usd
2016-06-30,101.2,67.9
2016-09-30,100.7,70.9
2016-12-31,101.3,82.6
"""

        assert m.header == ',CPI_rog,EXPORT_GOODS_bln_usd'
        # TODO: test this result for daily frequency - note it has missing
        # values, which is correct
        """,BRENT,USDRUR_CB
2016-06-01,48.81,65.9962
2016-06-02,49.05,66.6156
2016-06-03,48.5,66.7491
2016-06-04,,66.8529
2016-06-06,48.94,
2016-06-07,49.76,65.7894"""
