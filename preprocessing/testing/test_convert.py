'''
Tests for convert.py
'''

import yaml
import pandas as pd
import numpy as np
import nose
import vppreprocess

varInfoString = '''
    columns:
        include: [  'Variable Name',
                    'Value' ]
        renaming: { 'Variable Name' : 'variable',
                    'Value'         : 'value' }
'''
varInfo = yaml.load(varInfoString)

def test_select_cols():
    '''select_cols should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : ['-3.0', '2.0', '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    testDF = testDF[['Variable Name', 'Value', 'Unit']]
    expected_result = pd.DataFrame({
                           'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : ['-3.0', '2.0', '3.0', 'Text']
                       })
    expected_result = expected_result[['Variable Name', 'Value']]
    result = vppreprocess.select_cols(testDF, varInfo)
    assert result.equals(expected_result)

def test_rename_cols():
    '''rename_cols should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : ['-3.0', '2.0', '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    expected_result = pd.DataFrame({'variable' : ['A', 'A', 'B', 'Z'],
                           'value' : ['-3.0', '2.0', '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    result = vppreprocess.rename_cols(testDF, varInfo)
    assert result.equals(expected_result)
