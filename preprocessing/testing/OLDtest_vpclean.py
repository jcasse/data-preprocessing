'''
Tests for vpclean.py
'''

import yaml
import pandas as pd
import numpy as np
import nose
import vpclean

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
# Functions that remove rows from the data frame

def test_remove_vars_returns_expected_values():
    '''remove_vars should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                       'Value' : ['-3.0', '0.5', '3.0L', 'Text']
                       })
    expected_result = testDF.ix[0:2, :]
    result = vpclean.remove_vars(testDF, varInfo)
    assert result.equals(expected_result)


def test_remove_null_returns_expected_values():
    '''remove_null should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B'],
                       'Value' : ['-3.0', np.nan, '3.0L']
                       })
    expected_result = expected_result = testDF.ix[[0, 2], :]
    result = vpclean.remove_null(testDF)
    assert result.equals(expected_result)

def test_remove_alpha():
    '''remove_alpha should return the expected values'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'Z'],
        'Value' : ['-3.0', 'String', '2.0', np.nan, '3.0L', 'Text']
        })
    expected_result = testDF.ix[[0, 2, 3, 5], :]
    result = vpclean.remove_alpha(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_nonnumeric():
    '''remove_nonnumeric should return the expected values'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'Z'],
        'Value' : ['-3.0', 'String', '2.0', np.nan, '3.0L', 'Text']
        })
    expected_result = testDF.ix[[0, 2, 3, 5], :]
    result = vpclean.remove_nonnumeric(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_extreme():
    '''remove_extreme should return the expected values'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'B', 'Z'],
         'Value' : ['-3.0', '0.5', '2.0', np.nan, '1.0', '25', 'Text']
         })
    expected_result = testDF.ix[[1, 3, 4, 6], :]
    result = vpclean.remove_extreme(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_extreme_throws_if_input_nonnumeric():
    '''remove_extreme should throw exception if input is nonnumeric'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'B', 'Z'],
         'Value' : ['Text', '0.5', '2.0', np.nan, '1.0', '3.0L', 'Text']
         })
    nose.tools.assert_raises(Exception, vpclean.remove_extreme,
                             testDF, varInfo)


##############################################################################
# Functions that modify values in the data frame

def test_condition_var_names_returns_expected_values():
    '''condition_var_names should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A '],
                       'Value' : ['-3.0', '0.5']
                       })
    expected_result = testDF
    expected_result['Variable Name'] = ['A', 'A']
    result = vpclean.condition_var_names(testDF)
    assert result.equals(expected_result)

def test_convert_units():
    '''convert_units should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : ['-3.0', '2.0', '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    expected_result = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : [-3, 0.002, '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    result = vpclean.convert_units(testDF, varInfo)
    assert result.equals(expected_result)

def test_convert_units_throws_if_input_nonnumeric():
    '''convert_units should throw exception if input is nonnumeric'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : ['Text', '2.0', '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    nose.tools.assert_raises(Exception, vpclean.convert_units, testDF, varInfo)

def test_impute_dict_values():
    '''impute_dict_values should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['B', 'B'],
                       'Value' : ['small', 'large']
                       })
    expected_result = testDF.copy()
    expected_result['Value'] = [1.0, 25.0]
    result = vpclean.impute_dict_values(testDF, varInfo)
    result['Value'] = result['Value'].astype(np.float64)
    assert result.equals(expected_result)

def test_impute_dict_values_throws_exception_for_unmapped_input():
    '''impute_dict_values should throw exception for unmapped inputs'''
    testDF = pd.DataFrame({'Variable Name' : ['B', 'B'],
                       'Value' : ['small', 'no-such-value-in-the-mapping']
                       })
    #vpclean.impute_dict_values(testDF, varInfo)
    nose.tools.assert_raises(Exception, vpclean.impute_dict_values,
                             testDF, varInfo)

def test_convert_weird_numeric():
    '''convert_weird_numeric should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A'],
                       'Value' : ['-3.0', '<0.5']
                       })
    expected_result = testDF.copy()
    expected_result['Value'] = ['-3.0', '0.5']
    result = vpclean.convert_weird_numeric(testDF, varInfo)
    assert result.equals(expected_result)


def test_clip_values():
    '''clip_values should return the expected values'''
    varInfoString = '''
    A:
        min: 0
        max: 1
    B:
        min:
        max:
    '''
    varInfo = yaml.load(varInfoString)

    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'Z'],
         'Value' : ['-0.1', '0.5', '1.1', np.nan, '1.0', 'Text']
         })
    expected_result = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'Z'],
         'Value' : [0, 0.5, 1, np.nan, 1, 'Text']
         })
    result = vpclean.clip_values(testDF, varInfo)
    assert result.equals(expected_result)

def test_clip_values_throws_if_input_nonnumeric():
    '''clip_values should throw exception if input can't be cast to numeric'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'Z'],
                           'Value' : ['Text', '0.5', 'Text']})
    nose.tools.assert_raises(Exception, vpclean.clip_values, testDF, varInfo)

###############################################################################
# Helper functions

def test_flag_numeric():
    '''flag_numeric should return the expected flag array'''

    # Input is an numpy array
    test_array = np.array(['1', '2.1', 'a', '3.0L', np.nan])
    expected_result = np.array([True, True, False, False, True])
    result = vpclean.flag_numeric(test_array)
    assert np.array_equal(result, expected_result)

def test_flag_numeric_throws_if_input_not_ndarray():
    '''flag_numeric should raise exception if input is not an np.ndarray'''
    # Input is a pandas DataFrame
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A'],
         'Value' : ['1.0', '2.0L']
         })
    nose.tools.assert_raises(Exception, vpclean.flag_numeric, testDF['Value'])

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
    assert True  == vpclean.is_numeric_variable(varInfo, 'A')
    assert True  == vpclean.is_numeric_variable(varInfo, 'B')
    assert False == vpclean.is_numeric_variable(varInfo, 'C')
