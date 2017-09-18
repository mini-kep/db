"""Access functions to start/kill database in SQLalchemy and 
   and read/insert/update/delete rows.
"""

# TODO FIXME: needs better session manager, repeated code in access classes read/update
# TODO NEW: must have explicit upsert scenario 
# TO CONSIDER: conceptiually still mixed (date-freq-name key + value) operation 
#              and datapoint operation 


import sqlalchemy
from sqlalchemy.orm import sessionmaker
from datapoint import Datapoint, Base


def create_engine(engine_url='sqlite://'):
    """Defaults to in-memory sqlite engine."""
    return sqlalchemy.create_engine(engine_url, echo=True)

# create / drop tables

def create_tables(engine):
    Base.metadata.create_all(engine)


def drop_tables(engine):
    Base.metadata.drop_all(engine)

# session handling

def create_session_factory(engine):
    """Return a function, which is used to start a session.""" 
    return sessionmaker(bind=engine)

#TODO: enable session context manager
#      see usage in PonyORM in this repo
#      option 1: as in code below
#      option 2: with explicit __enter__ and __exit__ methods

#from contextlib import contextmanager
#
#@contextmanager
#def session_scope():
#    """Provide a transactional scope around a series of operations."""
#    session = Session()
#    try:
#        yield session
#        session.commit()
#    except:
#        session.rollback()
#        raise
#    finally:
#        session.close()
#
#
#def run_my_program():
#    with session_scope() as session:
#        ThingOne().go(session)
#        ThingTwo().go(session)
        


# session / row operations


def insert_one(session_factory, datapoint):

    session = session_factory()
    try:
        session.add(datapoint)
        session.commit()
        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()


def update_one(session_factory, condition, value):

    session = session_factory()
    try:
        result = session.query(Datapoint) \
            .filter_by(**condition) \
            .update({"value": value})
        session.commit()
        return result
    except:
        session.rollback()
        return False
    finally:
        session.close()


def delete_one(session_factory, condition):

    session = session_factory()
    try:
        result = session.query(Datapoint) \
            .filter_by(**condition) \
            .delete()
        session.commit()
        return result
    except:
        session.rollback()
        return False
    finally:
        session.close()


def find_by(session_factory, condition=None):

    session = session_factory()
    try:
        query = session.query(Datapoint)
        if condition is not None:
            return query.filter_by(**condition).all()
        else:
            return query.all()
    except:
        session.rollback()
        return False
    finally:
        session.close()

# FIXME: may delete
def strip_value(datapoint):
    return {k: v for k, v in datapoint.items() if k != "value"}


if __name__ == '__main__':

    engine = create_engine()
    create_tables(engine)
    session_factory = create_session_factory(engine)

    #sample data for datapoints
    d1 = dict(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
    d1_bis = dict(date="2014-03-31", freq='q', name="CPI_rog", value=102.0)
    d2 = dict(freq='m', name='BRENT', date='2017-09-20', value=50.25)
    
    # insert some non-existing datapoints
    is_inserted_1 = insert_one(session_factory, Datapoint(**d1))
    is_inserted_2 = insert_one(session_factory, Datapoint(**d2))
    assert (is_inserted_1 and is_inserted_2)

    # find a datapoint by date-freq-name    
    condition = dict(date="2014-03-31", freq='q', name="CPI_rog")
    found = find_by(session_factory, condition)
    assert isinstance(found, list)
    assert found[0].id > 0
    found[0].id = None
    assert found[0] == Datapoint(freq='q', name='CPI_rog', 
                                 date='2014-03-31', value=102.3)
    
    # update with value
    condition = dict(date="2014-03-31", freq='q', name="CPI_rog")
    is_updated = update_one(session_factory, condition, 102.0)
    assert is_updated

    # find a datapoint by date-freq-name
    condition = strip_value(d2)
    is_deleted = delete_one(session_factory, condition)
    assert is_deleted
    found2 = find_by(session_factory)
    assert isinstance(found2[0], Datapoint)

    drop_tables(engine)   
