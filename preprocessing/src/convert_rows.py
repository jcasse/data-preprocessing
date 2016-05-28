import pandas as pd
import numpy as np
import vppreprocess

def convert_to_epoch_time(data, time_col='End Time'):
    result = data.copy()
    # Using numpy:
    #   Note that numpy is timezone-aware, so we have to be careful
    result[time_col] = \
        (np.array(result[time_col].values, dtype="datetime64") - \
        np.datetime64('1970-01-01 00:00:00')) / \
        np.timedelta64(1,'s')

    return(result)

def convert_flagged_to_NaN(data, flags, col_name):
    result = data.copy()
    result.ix[flags, col_name] = np.nan
    return(result)

def convert_bad_times_to_empty_string(data, col_name):
    bad_time_flags = ~ vppreprocess.flag_datetime(data[col_name].values)
    result = data.copy()
    result.ix[bad_time_flags, col_name] = ''
    return(result)
