'''
Tests for convert_rows.py
'''

import pandas as pd
import numpy as np
import vppreprocess
import nose

# For epoch time, we should also test timezone issues.

def test_convert_to_epoch_time_returns_expected_values():
    '''convert_to_epoch_time should return the expected values'''
    test_data = pd.DataFrame({'time' : ['1970-01-02 00:00:00',
                                        '1970-01-01 01:00:00'],
                              'Value' : ['0', '1']
                             },
                             index = np.arange(2)+10)
    expected_result = pd.DataFrame({'time' : [86400, 3600.],
                                    'Value' : ['0', '1']
                             },
                             index = np.arange(2)+10)
    result = vppreprocess.convert_to_epoch_time(test_data, time_col='time')
    assert result.equals(expected_result)

    test_data = pd.DataFrame({'time' : ['1970-01-02 00:00:00',
                                        '1970-01-01 01:00:00',],
                              'Value' : ['0', '1']
                             }, index=pd.Int64Index([5, 6,]))
    expected_result = pd.DataFrame({'time' : [86400, 3600.],
                                    'Value' : ['0', '1']
                             }, index=pd.Int64Index([5, 6]))
    result = vppreprocess.convert_to_epoch_time(test_data, time_col='time')
    assert result.equals(expected_result)

    test_data = pd.DataFrame({'time' : ['1970-01-02 00:00:00',
                                        '1970-01-01 01:00:00',
                                        ''],
                              'Value' : ['0', '1', '2']
                             },
                             index = np.arange(3)+10)
    expected_result = pd.DataFrame({'time' : [86400, 3600, np.nan],
                                    'Value' : ['0', '1', '2']
                             },
                             index = np.arange(3)+10)
    result = vppreprocess.convert_to_epoch_time(test_data, time_col='time')
    assert result.equals(expected_result)

def test_convert_to_epoch_time_throws_expected_errors():
    '''convert_to_epoch_time should throw the expected errors'''
    test_data = pd.DataFrame({'End Time' : [' ']})
    nose.tools.assert_raises(Exception, vppreprocess.convert_to_epoch_time,
                             test_data, 'End Time')

    test_data = pd.DataFrame({'End Time' : ['bad string']})
    nose.tools.assert_raises(Exception, vppreprocess.convert_to_epoch_time,
                             test_data, 'End Time')

    test_data = pd.DataFrame({'End Time' : ['1970-01-02 00:00:00']})
    nose.tools.assert_raises(Exception, vppreprocess.convert_to_epoch_time,
                             test_data, 'nonexistent column')

def test_convert_flagged_to_NaN_returns_expected_values():
    test_data = pd.DataFrame({'End Time' : ['1970-01-02 00:00:00', 'NIL'],
                              'Value' : ['0', '1']
                             },
                             index = np.arange(2)+10)
    test_flags = np.array([False, True])

    expected_result = pd.DataFrame({'End Time' : ['1970-01-02 00:00:00', np.nan],
                                    'Value' : ['0', '1']
                             },
                             index = np.arange(2)+10)
    result = vppreprocess.convert_flagged_to_NaN(test_data,
                                            test_flags,
                                            col_name='End Time')
    assert result.equals(expected_result)

def test_convert_bad_times_to_empty_string_returns_expected_values():
    test_data = pd.DataFrame({'End Time' : ['1970-01-02 00:00:00', 'NIL'],
                              'Value' : ['0', '1']
                             })

    expected_result = pd.DataFrame({'End Time' : ['1970-01-02 00:00:00', ''],
                                    'Value' : ['0', '1']
                             })
    result = vppreprocess.convert_bad_times_to_empty_string(test_data,
                                                       col_name='End Time')
    assert result.equals(expected_result)
