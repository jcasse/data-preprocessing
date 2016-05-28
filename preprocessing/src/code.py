import pandas as pd
import numpy as np
import yaml
import os
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
#DRL - Data scrubbing functions. Due to the structure of the data files these
#       will typically have a two distinct formats
#
#      The first format will be for the removal of erroneous values:
#
#       mask_var will contain true entries for the current variable rows
#       mask_val will contain true entries for the curren variables bad values
#
#       We'll index the dataframe with the compliment of the bit-wise and mask
#
#       for examples: DF =  a, 1
#                           a, 2
#                           b, 1
#                           b, 2
#
#       and we want to remove b's with values > 1
#
#       mask_var = [false, false, true, true]
#       mask_val = [false, true, false, true]
#
#       the bitwise and mask would be:
#                 [false, false, false, true]
#
#       and the compliment mask would be:
#                 [true, true, true, false]
#
#       so that we drop the 4th element (as intended)
#
#      The second format will be for the clipping of long-tailed values
#
#       mask_var = df['Variable Name'] == 'variable'
#       df[mask_var] = df[mask_var].clip(minValue, maxValue)
##############################################################################

from pkg_resources import Requirement, resource_filename

def load_settings(name=None):
    '''
    Load settings dictionary.

    Returns a dict containing settings for data cleaning.

    Parameters
    ----------
    name : string, optional
        Specifies the settings to load. The default is None, which results in
        loading default settings. Alternative settings may be specified by name;
        run vpclean.show_available_settings() to get a list of available
        settings.
    '''
    if name is None:
        filename = resource_filename(Requirement.parse("vpclean"),
                                     "vpclean/data/settings_2015-11-06.yaml")
    else:
        settings_rel_path = os.path.join("vpclean/data", name)
        filename = resource_filename(Requirement.parse("vpclean"),
                                     settings_rel_path)
    settings = yaml.load(file(filename, 'r'))
    return(settings)

def show_available_settings():
    '''
    Load settings dictionary.

    Returns a dict containing settings for data cleaning.

    '''
    data_path = resource_filename(Requirement.parse("vpclean"),"vpclean/data/")
    available = subprocess.check_output(['ls', data_path]).split()
    return(available)

##############################################################################
# Functions that remove rows from the data frame

def remove_vars(dataDF, varInfo):
    '''
    Remove rows from dataDF for which the variable name is not in the keys
    of varInfo
    '''
    try:
        print 'dropping values not in %s...' % varInfo.keys()
        dataDF = dataDF[dataDF['Variable Name'].isin(varInfo.keys())]
    except AttributeError:
        print 'no information in yaml settings. skipping...'
    return dataDF

def remove_null(dataDF):
    '''
    Remove rows of dataDF for which the Value column has a null value
    '''
    dataDF = dataDF[~pd.isnull(dataDF['Value'])]
    return dataDF

def remove_alpha(dataDF, varInfo):
    '''
    For each variable in varInfo, if the alphaMask parameter (a regex)
    is in varInfo and is not None then remove all rows of dataDF for which
    the Value column matches the regex alphaMask
    '''
    mask_reject_alpha = np.array(np.zeros(dataDF.shape[0]), dtype='bool')
    for var in varInfo:
        if 'alphaMask' in varInfo[var]:
            print '\tremoving %s values from %s...' % \
                (varInfo[var]['alphaMask'], var)
            if varInfo[var]['alphaMask'] is not None:
                mask_var = dataDF['Variable Name'] == var
                mask_reject_alpha[np.where(mask_var)] =\
                    dataDF.loc[mask_var, 'Value'].str.contains(
                        varInfo[var]['alphaMask'], regex=True, na=False)
    dataDF = dataDF[~mask_reject_alpha]
    return dataDF

def remove_nonnumeric(dataDF, varInfo):
    '''
    Remove non-numeric values from variables that are supposed to be numeric.

    For each variable in varInfo, if the variable is a numeric variable
    (according to is_numeric_variable(varInfo, var)), then
    remove all rows of dataDF for which the Value column can not be
    cast to np.float
    '''
    mask_reject_nonnumeric = np.array(np.zeros(dataDF.shape[0]), dtype='bool')
    for var in varInfo:
        if is_numeric_variable(varInfo, var):
            mask_var = dataDF['Variable Name'] == var
            mask_reject_nonnumeric[np.where(mask_var)] =\
                ~flag_numeric(dataDF.loc[mask_var, 'Value'].values)
    dataDF = dataDF[~mask_reject_nonnumeric]
    return dataDF

def remove_extreme(dataDF, varInfo):
    '''
    For each variable in varInfo:
        - If the dropBelow parameter is in varInfo and is not None
        then remove all occurences of values < dropBelow
        - If the dropAbove parameter is in varInfo and is not None
        then remove all occurences of values > dropAbove
    If any non-numeric values are encountered, throw a ValueError exception
    '''
    mask_reject_below      = np.array(np.zeros(dataDF.shape[0]), dtype='bool')
    mask_reject_above      = np.array(np.zeros(dataDF.shape[0]), dtype='bool')

    for var in varInfo:
        print(var)
        if 'dropBelow' in varInfo[var] or 'dropAbove' in varInfo[var]:
            mask_var   = dataDF['Variable Name'] == var
            try:
                if 'dropBelow' in varInfo[var]:
                    if varInfo[var]['dropBelow'] is not None:
                        print '\tdropping values below %.1f...' % \
                            varInfo[var]['dropBelow']
                        mask_reject_below[np.where(mask_var)] =\
                            dataDF.loc[mask_var, 'Value'].astype(np.float) <\
                            varInfo[var]['dropBelow']
                if 'dropAbove' in varInfo[var]:
                    if varInfo[var]['dropAbove'] is not None:
                        print '\tdropping values above %.1f...' % \
                            varInfo[var]['dropAbove']
                        mask_reject_above[np.where(mask_var)] =\
                            dataDF.loc[mask_var, 'Value'].astype(np.float) >\
                            varInfo[var]['dropAbove']
            except ValueError as err:
                err.message = \
                    err.message + '\nError in vpclean.remove_extreme()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' values in the \'Value\' column of the data frame that' +\
                    ' could not be cast to float.'
                raise ValueError(err.message)
    dataDF = dataDF[~(mask_reject_above | mask_reject_below )]
    return dataDF

##############################################################################
# Functions that modify values in the data frame

def condition_var_names(dataDF):
    '''
    Remove trailing spaces from the values in the 'Variable Name' column
    '''
    dataDF['Variable Name'] = dataDF['Variable Name'].str.strip()
    return dataDF

def convert_units(dataDF, varInfo):
    '''
    For each variable in varInfo, if the unitConversionDict is in varInfo
    then normalize the values based on the unit key.
    If any non-numeric values are encountered, throw a ValueError exception
    '''
    for var in varInfo:
        if 'unitConversionDict' in varInfo[var]:
            print '\tnormalizing value units...'
            try:
                mask_var = (dataDF['Variable Name'] == var)
                #DRL - create a defaultdict of the values in the yaml which returns
                #       1 if no value specified (which, when we divide by, will not
                #       change the value in Value)
                unitConversionDict = defaultdict(lambda: 1)
                unitConversionDict.update(varInfo[var]['unitConversionDict'])

                #DRL - set the value of each row to Value / the unit conversion
                dataDF.loc[mask_var, 'Value'] = dataDF.loc[mask_var, 'Value'].astype(np.float)
                dataDF.loc[mask_var, 'Value'] = dataDF[mask_var].\
                    apply(lambda x: (x['Value'] / unitConversionDict[x['Unit']]), axis=1)
            #except:
            #    print 'SOMETHING WAS WRONG WITH THE %s UNIT CONVERSION DICTIONARY: %s'\
            #        % (var, varInfo[var]['unitConversionDict'])
            except ValueError as err:
                err.message = \
                    err.message + '\nError in vpclean.convert_units()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' values in the \'Value\' column of the data frame that' +\
                    ' could not be cast to float.'
                raise ValueError(err.message)
    return dataDF

def impute_dict_values(dataDF, varInfo):
    '''
    For each variable in varInfo, if the imputeDict parameter is in varInfo
    then impute values using the dictImputeKeyException function
    '''
    for var in varInfo:
        if 'imputeDict' in varInfo[var]:
            print '\timputing dictionary values...'
            try:
                mask_var = (dataDF['Variable Name'] == var)
                #dataDF['Value'][mask_var] = dataDF['Value'][mask_var].apply(\
                #    lambda x: DictImputeKeyException(x, varInfo[var]['imputeDict']))
                dataDF.loc[mask_var, 'Value'] = dataDF.loc[mask_var, 'Value'].apply(\
                    lambda x: varInfo[var]['imputeDict'][x])
            except KeyError as err:
                err.message = \
                    err.message + '\nError in vpclean.impute_dict_values()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' a value in the \'Value\' column of the data frame that' +\
                    ' does not have a mapping defined in the imputeDict.\n' + \
                    ' The values in the mapping are:\n\t' + \
                    ', '.join(varInfo[var]['imputeDict'].keys()) +\
                    '\nand the values you tried to map are:\n\t' + \
                    ', '.join(dataDF.loc[mask_var, 'Value'].unique())
                raise ValueError(err.message)
            except:
                print 'SOMETHING WAS WRONG WITH THE %s IMPUTE DICTIONARY: %s' \
                    % (var, varInfo[var]['imputeDict'])
    return dataDF

def convert_weird_numeric(dataDF, varInfo):
    '''
    For each variable in varInfo, if the variable is a numeric variable
    (according to is_numeric_variable(varInfo, var)), then
    remove the following characters from dataDF['Value']:
        > < +
    '''
    for var in varInfo:
        if is_numeric_variable(varInfo, var):
            mask_var                  = dataDF['Variable Name'] == var
            dataDF.loc[mask_var, 'Value'] = \
                dataDF.loc[mask_var, 'Value'].replace('>|<|\+', '', regex=True)
    return(dataDF)

def clip_values(dataDF, varInfo):
    '''
    For each variable in varInfo, if either the min or max parameter is in
    varInfo, clip the value to lie within (min, max).
    If min and max are keys in varInfo but the values are empty, do nothing.
    If any non-numeric values are encountered, throw a ValueError exception
    '''
    for var in varInfo:
        #DRL - clip everything with a min and max value
        if np.any(np.in1d(['min','max'], varInfo[var].keys())):
            try:
                #print '\tclipping values between %.1f and %.1f...' %\
                #    (varInfo[var]['min'], varInfo[var]['max'])
                mask_var = dataDF['Variable Name'] == var
                numeric_vals = dataDF.loc[mask_var, 'Value'].astype(np.float)
                dataDF.loc[mask_var, 'Value'] = numeric_vals.clip(varInfo[var]['min'],
                                                            varInfo[var]['max'])
            except ValueError as err:
                err.message = \
                    err.message + '\nError in vpclean.clip_values()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' values in the \'Value\' column of the data frame that' +\
                    ' could not be cast to float.'
                raise ValueError(err.message)
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

def is_numeric_variable(varInfo, var):
    '''
    Return True if any of the following are in varInfo[var]:
        min, max, dropBelow, dropAbove, unitConversionDict
    Otherwise return False.
    '''
    return(np.any(np.in1d( \
                ['min','max','dropBelow','dropAbove','unitConversionDict'],\
                varInfo[var].keys() )))

def _DictImputeKeyException(x, dictionary):
    try:
        return dictionary[x]
    except KeyError:
        return x
