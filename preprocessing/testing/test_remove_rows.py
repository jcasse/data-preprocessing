'''
Tests for remove_rows.py
'''

import pandas as pd
import yaml
import numpy as np
import vppreprocess


##############################################################################
# Functions that remove rows from the data frame

def test_remove_episodes_returns_expected_values():
    '''remove_vars should return the expected values'''
    varInfoString = '''
        episodes: [ '2_1',
                    '3_1' ]
    '''
    varInfo = yaml.load(varInfoString)
    testDF = pd.DataFrame({'patient_id_encounter' : ['1_1', '1_1', '2_1', '3_1'],
                        'Variable Name' : ['A', 'A', 'B', 'Z'],
                        'Value' : ['-3.0', '0.5', '3.0L', 'Text']
                       }, index = np.arange(4)+10)
    expected_result = testDF.iloc[2:4, :]
    result = vppreprocess.remove_episodes(testDF, varInfo)
    assert result.equals(expected_result)

def test_remove_null_returns_expected_values():
    '''remove_null should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B'],
                       'Value' : ['-3.0', np.nan, '3.0L']
                       })
    expected_result = expected_result = testDF.ix[[0, 2], :]
    result = vppreprocess.remove_null(testDF)
    assert result.equals(expected_result)

def test_remove_nonnumeric():
    '''remove_nonnumeric should return the expected values'''
    testDF = pd.DataFrame(
        {'Variable Name' : ['A', 'A', 'A', 'A', 'B', 'Z'],
        'Value' : ['-3.0', 'String', '2.0', np.nan, '3.0L', 'Text'],
        },
        index = np.arange(6)+10)
    expected_result = testDF.iloc[[0, 2, 3], :]
    result = vppreprocess.remove_nonnumeric(testDF)
    assert result.equals(expected_result)

def test_remove_nondatetime():
    '''test_remove_nondatetime return the expected values'''
    testDF = pd.DataFrame({
        'id' : ['1', '2', '3'],
        'time' : ['2015-01-01 00:00:00', 'NIL', '2015-01-01'] },
        index = np.arange(3)+10)
    expected_result = testDF.iloc[[0], :]
    result = vppreprocess.remove_nondatetime(testDF, col_name='time')
    assert result.equals(expected_result)

def test_remove_nondate():
    '''test_removenon_datetime return the expected values'''
    testDF = pd.DataFrame({
        'id' : ['1', '2', '3'],
        'time' : ['2015-01-01 00:00:00', 'NIL', '2015-01-01'] },
        index = np.arange(3)+10)
    expected_result = testDF.iloc[[2], :]
    result = vppreprocess.remove_nondate(testDF, col_name='time')
    assert result.equals(expected_result)
