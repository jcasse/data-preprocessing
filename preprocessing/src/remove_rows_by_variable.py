import pandas as pd
import numpy as np
import vppreprocess

def remove_vars(dataDF, varInfo):
    '''
    Remove rows from dataDF for which the variable name is not in the keys
    of varInfo
    '''
    resultDF = dataDF.copy()
    variables = varInfo['variables']
    try:
        selected = list({k for (k,v) in variables.items() if v is not None and 'include' in v})
        print 'dropping values not in %s...' % variables
        resultDF = resultDF.ix[resultDF['Variable Name'].isin(selected),:]
    except AttributeError:
        print 'no information in yaml settings. skipping...'
    return resultDF

def remove_unmapped_text_value_by_variable(dataDF, varInfo):
    '''
    For each variable defined in varInfo that has a mapping defined,
    removes rows for which the value is not in the mapping.
    '''
    resultDF = dataDF.copy()
    mask_remove = np.array(np.zeros(resultDF.shape[0]), dtype = 'bool')
    variables = varInfo['variables']
    for var in variables:
        if variables[var] is not None and 'encoding' in variables[var]:
            print '\tremoving unmpped text values...'
            mask_var = (resultDF['Variable Name'] == var)
            mask_remove[np.where(mask_var)] = ~np.in1d(resultDF.loc[mask_var, 'Value'], variables[var]['encoding'].keys())
    resultDF = resultDF[~mask_remove]
    return resultDF

def remove_alpha_by_variable(dataDF, varInfo):
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

def remove_nonnumeric_by_variable(dataDF, varInfo):
    '''
    Remove non-numeric values from variables that are supposed to be numeric.

    For each variable in varInfo, if the variable is a numeric variable
    (according to is_numeric_variable(varInfo, var)), then
    remove all rows of dataDF for which the Value column can not be
    cast to np.float
    '''
    mask_reject_nonnumeric = np.array(np.zeros(dataDF.shape[0]), dtype='bool')
    for var in varInfo:
        if vppreprocess.is_numeric_variable(varInfo, var):
            mask_var = dataDF['Variable Name'] == var
            mask_reject_nonnumeric[np.where(mask_var)] =\
                ~vppreprocess.flag_numeric(dataDF.loc[mask_var, 'Value'].values)
    dataDF = dataDF[~mask_reject_nonnumeric]
    return dataDF

def remove_extreme_by_variable(dataDF, varInfo):
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
        if 'dropBelow' in varInfo[var] or 'dropAbove' in varInfo[var]:
            print(var)
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
                    err.message + '\nError in ' +\
                    'vppreprocess.remove_extreme_by_variable()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' values in the \'Value\' column of the data frame that' +\
                    ' could not be cast to float.'
                raise ValueError(err.message)
    dataDF = dataDF.ix[~(mask_reject_above | mask_reject_below ),:]
    return dataDF
