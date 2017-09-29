"""Pure SQLAlchemy implementation of CRUD methods to:
   - start/kill database 
   - read/insert/update/delete rows.
   
Intent: make test scenarios applicable to production implementation either 
        as <https://docs.djangoproject.com/en/1.11/topics/db/models/>
        or <http://flask-sqlalchemy.pocoo.org/2.1/>.
  
"""

# TODO FIXME: needs better session manager, repeated code in access classes read/update
# TODO NEW: must have explicit upsert scenario 
# TO CONSIDER: conceptiually still mixed (date-freq-name key + value) operation  and datapoint operation 

# TODO: refactor tests, make them slim/closer to __main__ calls?


import sqlalchemy
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

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


@contextmanager
def scope(session_factory):
    """Provide a transactional scope around a series of operations."""    
    session = session_factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# context with no rollback       
class Session:
    def __init__(self, session_factory):
        self.session = session_factory()
        
    def __enter__(self):
        return self.session

    def __exit__(self, exception_type, exception_value, traceback):
        self.session.commit()
        self.session.close()


# session / row operations
def upsert_one(session_factory, condition, new_value):
    with scope(session_factory) as session:
        session.expire_on_commit = False
        result = session.query(Datapoint).filter_by(**condition).first()
        if result is None:
            session.add(Datapoint(**condition, value=new_value))
            return True
        else:
            if result.value != new_value:
                result.value = new_value
                return True
        return False


def insert_one(session_factory, datapoint):
    with scope(session_factory) as session:
        session.add(datapoint)
        return True
        

def update_one(session_factory, condition, value):
    with scope(session_factory) as session:
        result = session.query(Datapoint) \
            .filter_by(**condition) \
            .update({"value": value})
        return result


def delete_one(session_factory, condition):
    with scope(session_factory) as session:
        result = session.query(Datapoint) \
            .filter_by(**condition) \
            .delete()
        return result


def find_by(session_factory, condition=None):
    with scope(session_factory) as session:
        session.expire_on_commit = False
        query = session.query(Datapoint)
        if condition is not None:
            return query.filter_by(**condition).all()
        else:
            return query.all()    

# this version is obsolete now. use find_by instead.
#def find_by_(session_factory, condition=None):
#    session = session_factory()
#    try:
#        query = session.query(Datapoint)
#        if condition is not None:
#            return query.filter_by(**condition).all()
#        else:
#            return query.all()
#    except:
#        session.rollback()
#        return False
#    finally:
#        session.close()


        
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

    _ = find_by(session_factory, condition=dict(date="2014-03-31", freq='q', name="CPI_rog"))
    
    
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

    # upsert operation
    condition = dict(date="2014-03-31", freq='q', name="CPI_rog")
    upsert_one(session_factory, condition, 132.56)
    found_after_upsert = find_by(session_factory, condition)
    assert isinstance(found_after_upsert, list)
    assert len(found_after_upsert) == 1
    assert found_after_upsert[0].value == 132.56

    drop_tables(engine)   
