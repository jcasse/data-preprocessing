import pandas as pd
import numpy as np
import vppreprocess

def remove_episodes(dataDF, varInfo):
    '''
    Remove rows from dataDF for which the episode is not in the keys
    of varInfo
    '''
    resultDF = dataDF.copy()
    episodes = varInfo['episodes']
    try:
        #selected = list({k for (k,v) in episodes.items() if v is not None and 'include' in v})
        print 'dropping episodes not in %s...' % episodes
        resultDF = resultDF.ix[resultDF['patient_id_encounter'].isin(episodes),:]
    except AttributeError:
        print 'no information in yaml settings. skipping...'
    return resultDF

def remove_null(dataDF, value_col='Value'):
    '''
    Remove null values

    Remove rows of dataDF for which the specified column has a null value,
    i.e. for which pandas.isnull returns True.
    '''
    dataDF = dataDF[~pd.isnull(dataDF[value_col])]
    return dataDF

def remove_nonnumeric(dataDF, value_col='Value'):
    '''
    Remove non-numeric values

    Remove all rows of dataDF for which the specified column can not be
    cast to np.float. Note that NaNs will not be removed, because they have
    a float value.
    '''
    dataDF = dataDF.ix[vppreprocess.flag_numeric(dataDF[value_col].values),:]
    return dataDF

def remove_nondatetime(dataDF, col_name):
    '''
    Remove non-datetime values

    Remove all rows of dataDF for which the specified column can not be cast to
    np.datetime64 with units of 's' OR to np.datetime64('NaT') (not a time)
    '''
    dataDF = dataDF.ix[vppreprocess.flag_datetime(dataDF[col_name].values)]
    return(dataDF)

def remove_nondate(dataDF, col_name):
    '''
    Remove non-date values

    Remove all rows of dataDF for which the specified column can not be cast to
    np.datetime64 with units of 'D' OR to np.datetime64('NaT') (not a time)
    '''
    dataDF = dataDF.ix[vppreprocess.flag_date(dataDF[col_name].values)]
    return(dataDF)
