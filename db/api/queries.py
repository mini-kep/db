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

# FIXME: is this the same function? ---------------

def possible_names_values(freq):
    query = Datapoint.query
    if freq != 'all':
        query = query.filter_by(freq=freq)
    query = query.group_by(Datapoint.name).\
                  order_by(Datapoint.name).\
                  values(Datapoint.name)
    return [row.name for row in query] 


def datapoint_possible_names(freq):
    return Datapoint.query.\
        filter_by(freq=freq).\
        group_by(Datapoint.name).\
        values(Datapoint.name)    
        
# ---------------        
        

def get_boundary_date(freq, name, direction):
    sorter = dict(start=Datapoint.date,
                  end=Datapoint.date.desc())[direction]
    return Datapoint.query.filter_by(freq=freq, name=name) \
               .order_by(sorter) \
               .first()
