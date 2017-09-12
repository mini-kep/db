# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import TestCase
from sqlalchemy_plain_models.datapoint import Datapoint, Base


class DbTest(TestCase):

    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    def setUp(self):
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)


class BasicFilledDbSetup(DbTest):

    def setUp(self):
        super(BasicFilledDbSetup, self).setUp()
        x1 = Datapoint(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
        x2 = Datapoint(date="2017-03-16", freq='d', name="BRENT", value=50.56)
        self.session.add(x1)
        self.session.add(x2)
        self.session.commit()
        self.session.close()


class DbEmpty(DbTest):

    def test_initial_table_is_empty(self):
        count = self.session.query(Datapoint).count()
        assert count == 0


class BasicFilledDbUpdate(BasicFilledDbSetup):

    def test_update(self):
        # no specified data in DB currently
        result = self.session.query(Datapoint)\
            .filter_by(value=(50.56+10))\
            .all()
        assert len(result) == 0

        # update 1 row with specified data
        self.session.query(Datapoint).filter(Datapoint.name == "BRENT")\
            .update({"value": (50.56 + 10)})

        # assert that there's 1 row having specified data after update
        result = self.session.query(Datapoint)\
            .filter_by(value=(50.56 + 10))\
            .all()

        assert len(result) == 1
        datapoint = result[0]
        assert datapoint.name == "BRENT"
        assert datapoint.value == '60.56'


class BasicFilledDbDelete(BasicFilledDbSetup):

    def test_delete(self):
        count = self.session.query(Datapoint).count()
        assert count == 2

        self.session.query(Datapoint)\
            .filter(Datapoint.value == "102.3")\
            .delete()

        count = self.session.query(Datapoint).count()
        assert count == 1


class BasicFilledDbRead(BasicFilledDbSetup):

    def test_read(self):
        datapoints = self.session.query(Datapoint).all()
        assert len(datapoints) == 2

        x1 = Datapoint(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
        x2 = Datapoint(date="2017-03-16", freq='d', name="BRENT", value=50.56)

        for dp in datapoints:
            assert (dp.date == x1.date and dp.freq == x1.freq and dp.name == x1.name and float(dp.value) == x1.value) \
                   or (dp.date == x2.date and dp.freq == x2.freq and dp.name == x2.name and float(dp.value) == x2.value)
