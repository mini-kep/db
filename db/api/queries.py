from db.api.models import Datapoint


def select_datapoints(freq: str, name: str, start_date, end_date):
    data = Datapoint.query.filter_by(name=name, freq=freq).order_by(Datapoint.date)
    if start_date:
        data = data.filter(Datapoint.date >= start_date)
    if end_date:
        data = data.filter(Datapoint.date <= end_date)
    return data


def select_unique_frequencies():
    query = Datapoint.query.group_by(Datapoint.freq) \
                           .values(Datapoint.freq)
    return [row.freq for row in query]