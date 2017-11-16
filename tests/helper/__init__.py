import unittest
import datetime

from tests.test_basic import TestCaseBase
from db.helper import label


def test_split_label(self):
    assert label.split_label('GDP_bln_rub') == ('GDP', 'bln_rub')
    assert label.split_label('GDP_rog') == ('GDP', 'rog')
    assert label.split_label('PROD_E_TWh') == ('PROD_E', 'TWh')
    # note the () for tuple above
    with self.assertRaises(AssertionError):
        assert label.split_label('GDP_bln_rub') == 'GDP', 'bln_rub'


def test_extract_varname(self):
    assert label.extract_varname('GDP_bln_rub') == 'GDP'
    assert label.extract_varname('GDP_rog') == 'GDP'
    assert label.extract_varname('PROD_E_TWh') == 'PROD_E'


def test_extract_unit(self):
    assert label.extract_unit('GDP_bln_rub') == 'bln_rub'
    assert label.extract_unit('GDP_rog') == 'rog'
    assert label.extract_unit('PROD_E_TWh') == 'TWh'


if __name__ == '__main__':
    unittest.main()
