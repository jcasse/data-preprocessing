import pandas as pd
import numpy as np
import yaml
import os
import csv 
import subprocess
from collections import defaultdict

##############################################################################
# JW: TODO
#   For exceptions, make sure the error message is helpful. The user will
#   want to track down the problem in the data, or in the assumptions they
#   are making.
#
# Possible issues:
# 1) The data frame passed to these functions may be modified in place. Not sure
#    we really want that.
# 2) convert_units
#        Doesn't change the 'Unit' column, which can be misleading.
#        Doesn't complain if a unit isn't found in the conversion dict.
#        The dict is copied and pasted throughout the yaml file. Potential for copy and paste errors.
# 3) impute_dict_values
#       Can either leave unmapped values alone (David) or throw exception (me). What do we prefer?
# 4) Make it clear which functions operate on the entire data frame, vs.
#       operating only on those variables with entries in the settings file
# 5) Figure out what David's exception handling was supposed to do
#       DictImputeKeyException
#       "SOMETHING WAS WRONG WITH THE %s UNIT CONVERSION DICTIONARY:"

##############################################################################
# Functions that modify values in the data frame

def read_data(file_path):
    '''
    Reads csv file as text. Quotes in the csv file are interpreted as any
    regular character. Only commas have special meaning: as delimiters.
    Returns a pandas data frame, where every element is of type string.
    '''
    return(pd.read_csv(file_path,
            dtype = 'string',
            quoting = csv.QUOTE_NONE,
            keep_default_na = False))

def condition_var_names(dataDF):
    '''
    Remove trailing spaces from the values in the 'Variable Name' column
    '''
    dataDF['Variable Name'] = dataDF['Variable Name'].str.strip()
    return dataDF



###############################################################################
# Helper functions

def flag_numeric(arr):
    '''
    Return an array of the same length as the input, containing boolean flags
    of True where the input element can be cast to float, and False everywhere
    else
    '''
    if not isinstance(arr, np.ndarray):
        raise Exception
    numericFlags = np.array(np.ones(arr.shape[0]), dtype='bool')
    for i in range(0, arr.shape[0]):
        try:
            float(arr[i])
        except:
            numericFlags[i] = False
            continue
    return(numericFlags)

def flag_datetime(arr):
    '''
    Flag array locations where the value is a datetime, with days and times.

    Return an array of the same length as the input, containing boolean flags
    of
        - True where the input element can be cast to np.datetime64 with units
          of 's' AND is not np.datetime64('NaT') (not a time)
        - False everywhere else
    '''
    if not isinstance(arr, np.ndarray):
        raise Exception
    datetimeFlags = np.array(np.ones(arr.shape[0]), dtype='bool')
    for i in range(0, arr.shape[0]):
        try:
            # This will throw if arr[i] can't be cast to a time type.
            # But NaT is a time type! Let's flag that as not being a time
            dt = np.datetime64(arr[i], 's')
            if dt == np.datetime64('NaT'):
                datetimeFlags[i] = False
        except:
            datetimeFlags[i] = False
            continue
    return(datetimeFlags)

#def flag_datetime_2(arr):
#    '''
#    Flag array locations where the value is a datetime, with days and times.
#
#    Return an array of the same length as the input, containing boolean flags
#    of
#        - True where the input element is a string of the form
#          "YYYY-MM-DD HH:MM:SS"
#        - False everywhere else
#    '''
#    if not isinstance(arr, np.ndarray):
#        raise Exception
#    datetimeFlags = np.array(np.ones(arr.shape[0]), dtype='bool')
#    for i in range(0, arr.shape[0]):
#        try:
#            # This will throw if arr[i] can't be cast to a time type.
#            dt = datetime.datetime.strptime(arr[i], "%Y-%m-%d %H:%M:%S")
#        except:
#            datetimeFlags[i] = False
#            continue
#    return(datetimeFlags)

def flag_date(arr):
    '''
    Flag array locations where the value is a date (with no time).

    Return an array of the same length as the input, containing boolean flags
    of
        - True where the input element can be cast to np.datetime64 with units
          of 'D' AND is not np.datetime64('NaT') (not a time)
        - False everywhere else
    '''
    if not isinstance(arr, np.ndarray):
        raise Exception
    date_flags = np.array(np.ones(arr.shape[0]), dtype='bool')
    for i in range(0, arr.shape[0]):
        try:
            # This will throw if arr[i] can't be cast to a time type.
            # But NaT is a time type! Let's flag that as not being a time
            dt = np.datetime64(arr[i], 'D')
            if dt == np.datetime64('NaT'):
                date_flags[i] = False
        except:
            date_flags[i] = False
            continue
    return(date_flags)

def is_numeric_variable(varInfo, var):
    '''
    Return True if any of the following are in varInfo[var]:
        min, max, dropBelow, dropAbove, unitConversionDict
    Otherwise return False.
    '''
    return(np.any(np.in1d( \
                ['min','max','dropBelow','dropAbove','unitConversionDict'],\
                varInfo[var].keys() )))
