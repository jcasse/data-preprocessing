'''
Tests for vppreprocess.py
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
        encoding: {'small' : 1.0,
                     'large' : 25.0}
'''
varInfo = yaml.load(varInfoString)

def converted_data_frames_equal(mask_converted_rows, df1, df2):
    '''
    Helper function for testing. Compare data frames df1 and df2, which may
    have elements of type string that are unequal strings but represent equal
    numbers. mask_converted_rows is a boolean array indicating rows where the
    'Value' column should be interpreted as numeric.
        Return True if the data frames are equal after casting the
    'Value' column to float everywhere mask_converted_rows is True.
    '''
    df1 = df1.copy()
    df2 = df2.copy()
    df1.ix[mask_converted_rows,'Value'] = \
        df1.ix[mask_converted_rows,'Value'].values.astype('float')
    df2.ix[mask_converted_rows,'Value'] = \
        df2.ix[mask_converted_rows,'Value'].values.astype('float')
    return(df1.equals(df2))

def test_convert_units_by_variable():
    '''convert_units_by_variable should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : ['-3.0', '2.0', '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    expected_result = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : [-3, 0.002, '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    result = vppreprocess.convert_units_by_variable(testDF, varInfo)
    assert result.equals(expected_result)

def test_convert_units_by_variable_throws_if_input_nonnumeric():
    '''convert_units_by_variable should throw exception if input is nonnumeric'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'B', 'Z'],
                           'Value' : ['Text', '2.0', '3.0', 'Text'],
                           'Unit' : ['g', 'mg', None, None]
                       })
    nose.tools.assert_raises(Exception, vppreprocess.convert_units_by_variable,
                             testDF, varInfo)

def test_convert_dict_values_by_variable():
    '''convert_dict_values_by_variable should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['B', 'B'],
                       'Value' : ['small', 'large']
                       })
    expected_result = testDF.copy()
    expected_result['Value'] = [1.0, 25.0]
    result = vppreprocess.convert_dict_values_by_variable(testDF, varInfo)
    result['Value'] = result['Value'].astype(np.float64)
    assert result.equals(expected_result)

def test_convert_dict_values_throws_exception_for_unmapped_input():
    '''convert_dict_values_by_variable should throw exception for unmapped inputs'''
    testDF = pd.DataFrame({'Variable Name' : ['B', 'B'],
                       'Value' : ['small', 'no-such-value-in-the-mapping']
                       })
    #vppreprocess.impute_dict_values(testDF, varInfo)
    nose.tools.assert_raises(Exception, vppreprocess.convert_dict_values_by_variable,
                             testDF, varInfo)

def test_encode_text_values_by_variable():
    '''
    encode_text_values_by_variable should return the expected values
    '''
    varInfoString = '''
        variables:
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
    '''
    varInfo = yaml.load(varInfoString)
    testDF = pd.DataFrame({'Variable Name' : ['B', 'B'],
                       'Value' : ['small', 'large']
                       })
    expected_result = testDF.copy()
    expected_result['Value'] = [1.0, 25.0]
    result = vppreprocess.encode_text_values_by_variable(testDF, varInfo)
    result['Value'] = result['Value'].astype(np.float64)
    assert result.equals(expected_result)

def test_encode_text_values_throws_exception_for_unmapped_input():
    '''
    encode_text_values_by_variable should throw exception for unmapped inputs
    '''
    testDF = pd.DataFrame({'Variable Name' : ['B', 'B'],
                       'Value' : ['small', 'no-such-value-in-the-mapping']
                       })
    #vppreprocess.impute_dict_values(testDF, varInfo)
    nose.tools.assert_raises(Exception,
            vppreprocess.encode_text_values_by_variable, testDF, varInfo)

def test_convert_weird_numeric_by_variable():
    '''convert_weird_numeric_by_variable should return the expected values'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A'],
                       'Value' : ['-3.0', '<0.5']
                       })
    expected_result = testDF.copy()
    expected_result['Value'] = ['-3.0', '0.5']
    result = vppreprocess.convert_weird_numeric_by_variable(testDF, varInfo)
    assert result.equals(expected_result)


def test_clip_values_by_variable():
    '''clip_values_by_variable should return the expected values'''
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
    result = vppreprocess.clip_values_by_variable(testDF, varInfo)
    assert result.equals(expected_result)

def test_clip_values_throws_if_input_nonnumeric():
    '''clip_values should throw exception if input can't be cast to numeric'''
    testDF = pd.DataFrame({'Variable Name' : ['A', 'A', 'Z'],
                           'Value' : ['Text', '0.5', 'Text']})
    nose.tools.assert_raises(Exception, vppreprocess.clip_values_by_variable,
                             testDF, varInfo)

def test_age_normalize_by_variable():
    '''age_normalize_by_variable should return the expected values'''
    test_settings_string = '''
    age_groups:
        0-1 year: 0
        1-5 years: 1
    variables:
        Abdominal girth (cm):
            age_dependent: False
            quartile_1: 50
            median:     60
            quartile_3: 70
        Heart rate (bpm):
            age_dependent: True
            0-1 year:
                quartile_1: 119
                median:     136
                quartile_3: 152
            1-5 years:
                quartile_1: 105
                median:     122
                quartile_3: 139
    '''
    test_settings = yaml.load(test_settings_string)

    testDF = pd.DataFrame(
        {'patient_id_encounter': ['1', '1', '2'],
         'Variable Name'       : ['Abdominal girth (cm)', 'Heart rate (bpm)',
                                  'Heart rate (bpm)'],
         'Value'               : ['40', '103', '139'],
         'End Time'            : ['2015-02-02 12:00:00', '2015-02-02 12:00:00',
                                  '2017-07-07 12:00:00']
         }, index=np.arange(3)+6)
    test_encinfo = pd.DataFrame(
        {'patient_id_encounter'    : ['1', '2'],
         'Episode Start Timestamp' : ['2015-02-02 10:00:00',
                                      '2017-07-07 10:00:00']
         })
    expected = pd.DataFrame(
        {'patient_id_encounter': ['1', '1', '2'],
         'Variable Name'       : ['Abdominal girth (cm)', 'Heart rate (bpm)',
                                  'Heart rate (bpm)'],
         'Value'               : ['-2.0', '-2.0', '1.0'],
         'End Time'            : ['2015-02-02 12:00:00', '2015-02-02 12:00:00',
                                  '2017-07-07 12:00:00']
         }, index=np.arange(3)+6)
    result = vppreprocess.age_normalize_by_variable(testDF, test_encinfo,
                                                    test_settings)
    mask_converted_rows = np.array([True, True, True])
    assert converted_data_frames_equal(mask_converted_rows, result, expected)

    testDF = pd.DataFrame(
        {'patient_id_encounter': ['1', '1', '2'],
         'Variable Name'       : ['Abdominal girth (cm)', 'Heart rate (bpm)',
                                  'B'],
         'Value'               : ['40', '103', 'small'],
         'End Time'            : ['2015-02-02 12:00:00', '2015-02-02 12:00:00',
                                  '2017-07-07 12:00:00']
         })
    test_encinfo = pd.DataFrame(
        {'patient_id_encounter'    : ['1', '2'],
         'Episode Start Timestamp' : ['2015-02-02 10:00:00',
                                      '2017-07-07 10:00:00']
         })
    expected = pd.DataFrame(
        {'patient_id_encounter': ['1', '1', '2'],
         'Variable Name'       : ['Abdominal girth (cm)', 'Heart rate (bpm)',
                                  'B'],
         'Value'               : ['-2.0', '-2.0', 'small'],
         'End Time'            : ['2015-02-02 12:00:00', '2015-02-02 12:00:00',
                                  '2017-07-07 12:00:00']
         })
    result = vppreprocess.age_normalize_by_variable(testDF, test_encinfo,
                                                    test_settings)
    mask_converted_rows = np.array([True, True, False])
    assert converted_data_frames_equal(mask_converted_rows, result, expected)

def test_age_normalize_by_variable_throws_if_input_nonnumeric():
    '''age_normalize_by_variable should throw exception if input is nonnumeric'''
    test_settings_string = '''
    age_groups:
        0-1 year: 0
        1-5 years: 1
    variables:
        Abdominal girth (cm):
            age_dependent: False
            quartile_1: 50
            median:     60
            quartile_3: 70
        Heart rate (bpm):
            age_dependent: True
            0-1 year:
                quartile_1: 119
                median:     136
                quartile_3: 152
            1-5 years:
                quartile_1: 105
                median:     122
                quartile_3: 139
    '''
    test_settings = yaml.load(test_settings_string)

    testDF = pd.DataFrame(
        {'patient_id_encounter': ['1', '1', '2'],
         'Variable Name'       : ['Abdominal girth (cm)', 'Heart rate (bpm)',
                                  'Heart rate (bpm)'],
         'Value'               : ['40', '103', 'not numeric!'],
         'End Time'            : ['2015-02-02 12:00:00', '2015-02-02 12:00:00',
                                  '2017-07-07 12:00:00']
         }, index=np.arange(3)+6)
    test_encinfo = pd.DataFrame(
        {'patient_id_encounter'    : ['1', '2'],
         'Episode Start Timestamp' : ['2015-02-02 10:00:00',
                                      '2017-07-07 10:00:00']
         })
    nose.tools.assert_raises(Exception, vppreprocess.age_normalize_by_variable,
                             testDF, test_encinfo, test_settings)
