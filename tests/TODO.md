0. review <https://github.com/mini-kep/intro/blob/master/testing_guidelines/README.md>
1. read code at test_basic.py
   - comment if necessary
   - use this base class in all tests
2. todo: from test_views_old.py bring tests to **test_views.py** +
         refactor them to use class TestCaseBase
   (do this carefully as tests in test_views_old.py are not too good)
3. split test_datapoints.py at the end we shall need (all based on test_basic.TestCaseBase) 
   - test_views.py
   - test_util.py
   - test_queries.py 
4. not todo: test_errors.py + test_model.py  