# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import TestCase
from sqla_demo.datapoint import Datapoint, Base


class Test_DatabaseSchema(TestCase):

    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    def setUp(self):
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_Datapoint_table_is_empty_after_init(self):
        query = self.session.query(Datapoint)
        assert query.count == 0



class FilledDatabase(Test_DatabaseSchema):

    def setUp(self):
        # call create_all
        super(Test_DatabaseSchema, self).setUp()
        # datpoints
        self.x1 = Datapoint(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
        self.x2 = Datapoint(date="2017-03-16", freq='d', name="BRENT", value=50.56)
        # add and close session 
        for x in self.x1, self.x2:
            self.session.add(x)
        self.session.commit()
        self.session.close()


#filter by just one variable is not good
#TODO - CRITICAL: update/delete must operate on full datapoint, not querying
#                 not querying just one of parameters in key

#TODO - CRITICAL: add combined primary key [freq-varname-date]

class Test_Update(FilledDatabase):

    # TODO: separate to several methods each testing one thing, 
    #       one assert per test metod 
    #       tests should have long naming with what-when-result
    
    def setUp(self):
        self.unseen_value = 50.56 + 10 
    
    def test_update(self):
        
        # this is one testing method
        
        # no specified data in DB currently
        result = self.session.query(Datapoint)\
            .filter_by(value=(self.unseen_value))\
            .all()
        assert len(result) == 0

        # this is another testing method         

        # update 1 row with specified data
        self.session.query(Datapoint).filter(Datapoint.name == "BRENT")\
            .update({"value": (self.unseen_value )})

        # assert that there's 1 row having specified data after update
        result = self.session.query(Datapoint)\
            .filter_by(value=(self.unseen_value))\
            .all()

        assert len(result) == 1
        datapoint = result[0]
        assert datapoint.name == "BRENT"
        assert datapoint.value == '60.56'


class Test_Delete(FilledDatabase):

    def test_before_delete_database_has_two_rows(self):
        count = self.session.query(Datapoint).count()
        assert count == 2

    def test_aftere_delete_database_has_two_rows(self):
        self.session.query(Datapoint)\
            .filter(Datapoint.value == "102.3")\
            .delete()

        count = self.session.query(Datapoint).count()
        assert count == 1


class Test_Read(FilledDatabase):

    # FIXME CRITICAL: must assert on getting same values from database, not Datapoint-to_datapoint identity
    # ERROR: float is eaten into a string, tests do not catch this.  
    def test_read(self):
        datapoints = self.session.query(Datapoint).all()
        assert len(datapoints) == 2

        x1 = Datapoint(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
        x2 = Datapoint(date="2017-03-16", freq='d', name="BRENT", value=50.56)

        for dp in datapoints:
            # FIXME: no compined assert like this, too long, needs refactroing 
            assert (dp.date == x1.date and dp.freq == x1.freq and dp.name == x1.name and float(dp.value) == x1.value) \
                   or (dp.date == x2.date and dp.freq == x2.freq and dp.name == x2.name and float(dp.value) == x2.value)

#TODO - CRITICAL: add combined primary key [freq-varname-date]

# TODO: run tests from main

