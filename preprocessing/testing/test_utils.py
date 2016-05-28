'''
Tests for utils.py
'''

import yaml
import pandas as pd
import numpy as np
import nose
import vppreprocess

varInfoString = '''
    A:
        alphaMask: '[a-zA-Z]|\.$'
        min: 0
        max: 1
        dropBelow: -1.0
        dropAbove: 1.5
        unitConversionDict: {'None'      : 1000,
                             'g'         : 1,
                             'mg'        : 1000}
        impute: 0
    B:
        alphaMask: '[a-zA-Z]|\.$'
        min: 1
        max: 2
        dropBelow: 0
        dropAbove: 5
        impute: 0
        imputeDict: {'small' : 1.0,
                     'large' : 25.0}
'''
varInfo = yaml.load(varInfoString)

##############################################################################
# Functions that modify values in the data frame

def test_condition_var_names_returns_expected_values():
    '''condition_var_names should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A '],
                       'Value' : ['-3.0', '0.5']
                       })
    expected_result = testDF
    expected_result['Variable Name'] = ['A', 'A']
    result = vppreprocess.condition_var_names(testDF)
    assert result.equals(expected_result)


###############################################################################
# Helper functions

def test_flag_numeric():
    '''flag_numeric should return the expected flag array'''

    # Input is an numpy array
    test_array = np.array(['1', '2.1', 'a', '3.0L', np.nan])
    expected_result = np.array([True, True, False, False, True])
    result = vppreprocess.flag_numeric(test_array)
    assert np.array_equal(result, expected_result)

def test_flag_numeric_throws_if_input_not_ndarray():
    '''flag_numeric should raise exception if input is not an np.ndarray'''
    # Input is a pandas DataFrame
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A'],
         'Value' : ['1.0', '2.0L']
         })
    nose.tools.assert_raises(Exception, vppreprocess.flag_numeric, testDF['Value'])

def test_flag_datetime():
    '''flag_datetime should return the expected flag array'''

    # Input is an numpy array
    test_array = np.array(['2015-03-08 01:00:00',
                           '2015-07-23',
                           '',
                           ' ',
                           'NIL',
                           np.nan])
    expected_result = np.array([True, False, False, False, False, False])
    result = vppreprocess.flag_datetime(test_array)
    assert np.array_equal(result, expected_result)

def test_flag_date():
    '''flag_date should return the expected flag array'''

    # Input is an numpy array
    test_array = np.array(['2015-03-08 01:00:00',
                           '2015-07-23',
                           '',
                           'NIL',
                           np.nan])
    expected_result = np.array([False, True, False, False, False])
    result = vppreprocess.flag_date(test_array)
    assert np.array_equal(result, expected_result)

def test_is_numeric_variable_returns_correct_values():
    '''is_numeric_variable return the expected flag array'''
    varInfoString = '''
    A:
        min: 0
        unitConversionDict: {'None'      : 1000,
                             'g'         : 1,
                             'mg'        : 1000}
    B:
        dropAbove:
    C:
        impute: something
    '''
    varInfo = yaml.load(varInfoString)
    assert True  == vppreprocess.is_numeric_variable(varInfo, 'A')
    assert True  == vppreprocess.is_numeric_variable(varInfo, 'B')
    assert False == vppreprocess.is_numeric_variable(varInfo, 'C')
