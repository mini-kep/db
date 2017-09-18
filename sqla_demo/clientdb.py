"""Access functions to start database in SQLa and read/insert/update/delete rows.

SQLa = sqlalchemy
"""

import sqlalchemy
from sqlalchemy.orm import sessionmaker
#FIXME: do we need to import Base from Datapoint?
from sqla_demo.datapoint import Datapoint, Base


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

# FIXME: this should be explicit dictionary, not reverse reading from datapoint
def get_datapoint_condition(datapoint):
    return {k: v for k, v in datapoint.items() if k != "value"}


if __name__ == '__main__':

    engine = create_engine()
    create_tables(engine)
    session_factory = create_session_factory(engine)

    dp1_raw = dict(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
    result_of_insert = insert_one(session_factory, Datapoint(**dp1_raw))

    dp1_raw_with_updated_value = {**dp1_raw}
    condition = get_datapoint_condition(dp1_raw_with_updated_value)
    result_of_find_by = find_by(session_factory, condition)

    condition = get_datapoint_condition(dp1_raw_with_updated_value)
    result_of_update_one = update_one(session_factory, condition, dp1_raw_with_updated_value["value"])

    condition = get_datapoint_condition(dp1_raw)
    result_of_delete_one = delete_one(session_factory, condition)
    result_of_find_by = find_by(session_factory)

    drop_tables(engine)
