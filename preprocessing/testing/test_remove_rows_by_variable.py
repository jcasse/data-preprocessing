'''
Tests for vppreprocess.py
'''

import pandas as pd
import numpy as np
import yaml
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
        encoding: {'small' : 1.0,
                     'large' : 25.0}
        include:
'''
varInfo = yaml.load(varInfoString)

##############################################################################
# Functions that remove rows from the data frame

def test_remove_vars_returns_expected_values():
    '''remove_vars should return the expected values'''
    varInfoString = '''
        variables:
            A:
            B:
                encoding: {'small' : 1.0,
                             'large' : 25.0}
                include:
    '''
    varInfo = yaml.load(varInfoString)
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                       'Value' : ['-3.0', '0.5', '3.0L', 'Text']
                       }, index = np.arange(4)+10)
    expected_result = testDF.iloc[2:3, :]
    result = vppreprocess.remove_vars(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_unmapped_text_value_by_variable():
    '''
    remove_unmapped_text_value_by_variable should return the expected values
    '''
    varInfoString = '''
        variables:
            A:
            B:
                encoding: {'small' : 1.0,
                             'large' : 25.0}
                include:
    '''
    varInfo = yaml.load(varInfoString)
    testDF = pd.DataFrame(
        {'Variable Name' : ['B', 'A', 'A', 'A', 'B', 'Z'],
        'Value' : ['small', 'large', '2.0', '', 'unmapped', 'large']
        }, index = np.arange(6)+10)
    expected_result = testDF.iloc[[0, 1, 2, 3, 5], :]
    result = vppreprocess.remove_unmapped_text_value_by_variable(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_alpha_by_variable():
    '''remove_alpha_by_variable should return the expected values'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'Z'],
        'Value' : ['-3.0', 'String', '2.0', np.nan, '3.0L', 'Text']
        }, index = np.arange(6)+10)
    expected_result = testDF.iloc[[0, 2, 3, 5], :]
    result = vppreprocess.remove_alpha_by_variable(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_nonnumeric_by_variable():
    '''remove_nonnumeric_by_variable should return the expected values'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'Z'],
        'Value' : ['-3.0', 'String', '2.0', np.nan, '3.0L', 'Text']
        }, index = np.arange(6)+10)
    expected_result = testDF.iloc[[0, 2, 3, 5], :]
    result = vppreprocess.remove_nonnumeric_by_variable(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_extreme_by_variable():
    '''remove_extreme_by_variable should return the expected values'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'B', 'Z'],
         'Value' : ['-3.0', '0.5', '2.0', np.nan, '1.0', '25', 'Text']
         }, index = np.arange(7)+10)
    expected_result = testDF.iloc[[1, 3, 4, 6], :]
    result = vppreprocess.remove_extreme_by_variable(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_extreme_by_variable_throws_if_input_nonnumeric():
    '''remove_extreme_by_variable should throw exception if input is nonnumeric'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'B', 'Z'],
         'Value' : ['Text', '0.5', '2.0', np.nan, '1.0', '3.0L', 'Text']
         }, index = np.arange(7)+10)
    nose.tools.assert_raises(Exception, vppreprocess.remove_extreme_by_variable,
                             testDF, varInfo)
