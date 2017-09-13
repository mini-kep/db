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


class Test_DatabaseEmpty(Test_DatabaseSchema):

    def test_datapoint_table_is_empty_after_init(self):
        query = self.session.query(Datapoint)
        assert query.count() == 0


class FilledDatabase(Test_DatabaseSchema):

    def setUp(self):
        # call create_all
        super(FilledDatabase, self).setUp()
        # datapoints
        self.datapoint1_values = dict(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
        self.datapoint2_values = dict(date="2017-03-16", freq='d', name="BRENT", value=50.56)

        x1 = Datapoint(**self.datapoint1_values)
        x2 = Datapoint(**self.datapoint2_values)
        # add and close session
        for x in x1, x2:
            self.session.add(x)
        self.session.commit()
        self.session.close()

    def test_unique_constraint_acting_on_insert(self):

        with self.assertRaises(Exception):
            self.session.add(Datapoint(**self.datapoint1_values))
            self.session.commit()
            self.session.close()

        self.session.rollback()

    def get_datapoint_condition(self, datapoint):
        return {k: v for k, v in datapoint.items() if k != "value"}


#filter by just one variable is not good
#TODO - CRITICAL: update/delete must operate on full datapoint, not querying
#                 not querying just one of parameters in key

#TODO - CRITICAL: add combined primary key [freq-varname-date]

class Test_Update(FilledDatabase):

    def setUp(self):
        super(Test_Update, self).setUp()
        self.datapoint_with_updated_values = {**self.datapoint1_values}
        self.datapoint_with_updated_values["value"] = 15.6

    def test_before_update_database_has_no_specified_row(self):

        # no specified data in DB currently
        count = self.session.query(Datapoint)\
            .filter_by(**self.datapoint_with_updated_values)\
            .count()
        assert count == 0

    def test_update(self):
        # update 1 row with specified data

        condition = self.get_datapoint_condition(self.datapoint1_values)

        self.session.query(Datapoint).filter_by(**condition) \
            .update({"value": self.datapoint_with_updated_values["value"]})

        # assert that there's 1 row only having specified data after update
        count = self.session.query(Datapoint) \
            .filter_by(**condition) \
            .count()
        assert count == 1

    def test_unique_constraint_acting_on_update(self):

        # test that there cannot be the two equal datasets described by Datapoint's UniqueConstraint
        with self.assertRaises(Exception):
            self.session.query(Datapoint).filter_by(**self.get_datapoint_condition(self.datapoint1_values)) \
                .update(**self.datapoint2_values)
            self.session.commit()
            self.session.close()


class Test_Delete(FilledDatabase):

    def test_before_delete_database_has_two_rows(self):
        count = self.session.query(Datapoint).count()
        assert count == 2

    def test_after_delete_database_has_one_row(self):

        condition = self.get_datapoint_condition(self.datapoint2_values)

        self.session.query(Datapoint)\
            .filter_by(**condition)\
            .delete()

        count = self.session.query(Datapoint).count()
        assert count == 1


class Test_Read(FilledDatabase):

    def test_filled_database_has_two_rows_only(self):
        count = self.session.query(Datapoint).count()
        assert count == 2

    def test_filled_database_has_specified_datapoint1(self):

        condition = self.get_datapoint_condition(self.datapoint1_values)

        count = self.session.query(Datapoint) \
            .filter_by(**condition) \
            .count()
        assert count == 1

    def test_filled_database_has_specified_datapoint2(self):

        condition = self.get_datapoint_condition(self.datapoint2_values)

        count = self.session.query(Datapoint) \
            .filter_by(**condition) \
            .count()
        assert count == 1


class Test_Insert(FilledDatabase):

    def setUp(self):
        super(Test_Insert, self).setUp()
        self.non_existed_datapoint_values = dict(date="2017-07-10", freq='q', name="CPI_rog", value=77.7)

    def test_database_has_no_new_datapoint_which_has_not_been_inserted_yet(self):

        condition = self.get_datapoint_condition(self.non_existed_datapoint_values)

        count = self.session.query(Datapoint) \
            .filter_by(**condition) \
            .count()
        assert count == 0

    def test_database_has_new_datapoint_after_it_has_been_inserted(self):

        # tests that insert of new unique row actually works
        new_datapoint = Datapoint(**self.non_existed_datapoint_values)
        self.session.add(new_datapoint)
        self.session.commit()
        self.session.close()

        condition = self.get_datapoint_condition(self.non_existed_datapoint_values)

        count = self.session.query(Datapoint) \
            .filter_by(**condition) \
            .count()
        assert count == 1

    def test_database_has_new_datapoint_with_proper_value_after_it_has_been_inserted(self):

        # tests that insert of new unique row actually works (value testing)
        new_datapoint = Datapoint(**self.non_existed_datapoint_values)
        self.session.add(new_datapoint)
        self.session.commit()
        self.session.close()

        condition = self.get_datapoint_condition(self.non_existed_datapoint_values)

        result = self.session.query(Datapoint) \
            .filter_by(**condition) \
            .one()
        assert result.value == self.non_existed_datapoint_values["value"]

    def test_duplicates_not_allowed_on_insert(self):

        # this datapoint already exists in the Database
        datapoint = Datapoint(**self.datapoint1_values)

        with self.assertRaises(Exception):
            self.session.add(datapoint)
            self.session.commit()
            self.session.close()

        self.session.rollback()


#TODO - CRITICAL: add combined primary key [freq-varname-date]

# TODO: run tests from main
