# -*- coding: utf-8 -*-
from unittest import TestCase

from sqlalchemy import exc
import clientdb as clientdb


class TestClientDB(TestCase):

    def setUp(self):
        self.engine = clientdb.create_engine()
        clientdb.create_tables(self.engine)
        self.session_factory = clientdb.create_session_factory(self.engine)

    def tearDown(self):
        clientdb.drop_tables(self.engine)


class TestFilledClientDB(TestClientDB):

    def setUp(self):
        super(TestFilledClientDB, self).setUp()
        self.dp1_raw = dict(date="2014-03-31", freq='q', name="CPI_rog", value=102.3)
        self.dp2_raw = dict(date="2017-03-16", freq='d', name="BRENT", value=50.56)
        for dpx in self.dp1_raw, self.dp2_raw:
            clientdb.insert_one(self.session_factory, clientdb.Datapoint(**dpx))


class TestUpdateClientDB(TestFilledClientDB):

    def setUp(self):
        super(TestUpdateClientDB, self).setUp()
        self.dp1_raw_with_updated_value = {**self.dp1_raw}
        self.dp1_raw_with_updated_value["value"] += 11.12
        self.non_existing_dp_raw = dict(date="2000-03-31", freq='q', name="CPII_rog", value=32.0)

    def test_before_update_row_has_old_value(self):
        condition = clientdb.strip_value(self.dp1_raw_with_updated_value)
        # tests that the specified row has "old" value before update
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 1 and result[0].value != self.dp1_raw_with_updated_value["value"]

    def test_after_update_row_has_new_value(self):
        # update 1 row with specified data
        condition = clientdb.strip_value(self.dp1_raw_with_updated_value)
        clientdb.update_one(self.session_factory, condition, self.dp1_raw_with_updated_value["value"])
        # tests that the specified row has "new" value after update
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 1 and result[0].value == self.dp1_raw_with_updated_value["value"]

    def test_update_non_existing_row_has_no_effect(self):
        condition = clientdb.strip_value(self.non_existing_dp_raw)
        clientdb.update_one(self.session_factory, condition, self.non_existing_dp_raw["value"])
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 0


class TestInsertClientDB(TestFilledClientDB):

    def setUp(self):
        super(TestInsertClientDB, self).setUp()
        self.dp_new_raw = dict(date="2015-03-31", freq='q', name="some_new_name", value=2.44)
        self.dp_new = clientdb.Datapoint(**self.dp_new_raw)

    def test_database_has_no_new_datapoint_which_has_not_been_inserted_yet(self):
        result = clientdb.find_by(self.session_factory, self.dp_new_raw)
        assert len(result) == 0

    def test_insert_duplicate_datapoints_fails(self):
        for dpx in self.dp1_raw, self.dp2_raw:
            dp_copy = clientdb.Datapoint(**dpx)
            self.assertRaises(exc.IntegrityError, clientdb.insert_one, self.session_factory, dp_copy)

    def test_database_has_new_datapoint_after_it_has_been_inserted(self):
        clientdb.insert_one(self.session_factory, self.dp_new)
        result = clientdb.find_by(self.session_factory, self.dp_new_raw)
        assert len(result) == 1 and result[0].value == self.dp_new_raw["value"]


class TestDeleteClientDB(TestFilledClientDB):

    def setUp(self):
        super(TestDeleteClientDB, self).setUp()
        self.non_existing_dp_raw = dict(date="2000-03-31", freq='q', name="CPII_rog", value=32.0)

    def test_before_delete_database_has_two_rows(self):
        result = clientdb.find_by(self.session_factory)
        assert len(result) == 2

    def test_after_delete_one_row_database_has_one_row(self):
        condition = clientdb.strip_value(self.dp2_raw)
        clientdb.delete_one(self.session_factory, condition)
        result = clientdb.find_by(self.session_factory)
        assert len(result) == 1

    def test_delete_non_existing_row_has_no_effect(self):
        condition = clientdb.strip_value(self.non_existing_dp_raw)
        clientdb.delete_one(self.session_factory, condition)
        result = clientdb.find_by(self.session_factory)
        assert len(result) == 2


class TestReadClientDB(TestFilledClientDB):

    def test_filled_database_has_two_rows_only(self):
        result = clientdb.find_by(self.session_factory)
        assert len(result) == 2

    def test_filled_database_has_specified_datapoint1(self):
        condition = clientdb.strip_value(self.dp1_raw)
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 1

    def test_filled_database_has_specified_datapoint2(self):
        condition = clientdb.strip_value(self.dp2_raw)
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 1


class TestUpsertClientDB(TestFilledClientDB):

    def setUp(self):
        super(TestUpsertClientDB, self).setUp()
        self.dp1_updated_value = self.dp1_raw["value"] + 12.31
        self.dp_new_raw = dict(date="2015-03-31", freq='q', name="some_new_name", value=2.49)

    def test_before_upsert_the_old_row_has_old_value(self):
        condition = clientdb.strip_value(self.dp1_raw)
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 1 and result[0].value != self.dp1_updated_value

    def test_after_upsert_the_old_row_has_new_value(self):
        condition = clientdb.strip_value(self.dp1_raw)
        clientdb.upsert_one(self.session_factory, condition, self.dp1_updated_value)
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 1 and result[0].value == self.dp1_updated_value

    def test_before_upsert_database_has_no_new_datapoint_which_has_not_been_inserted_yet(self):
        condition = clientdb.strip_value(self.dp_new_raw)
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 0

    def test_after_upsert_database_has_new_datapoint_after_it_has_been_inserted(self):
        condition = clientdb.strip_value(self.dp_new_raw)
        clientdb.upsert_one(self.session_factory, condition, self.dp_new_raw["value"])
        result = clientdb.find_by(self.session_factory, condition)
        assert len(result) == 1 and result[0].value == self.dp_new_raw["value"]
