import pandas as pd
import numpy as np
import operator
from collections import defaultdict
import vppreprocess

def convert_units_by_variable(dataDF, varInfo):
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
                    err.message + '\nError in vppreprocess.convert_units()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' values in the \'Value\' column of the data frame that' +\
                    ' could not be cast to float.'
                raise ValueError(err.message)
    return dataDF

def convert_dict_values_by_variable(dataDF, varInfo):
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
                    err.message + '\nError in vppreprocess.impute_dict_values()' +\
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

def encode_text_values_by_variable(dataDF, varInfo):
    '''
    For each variable in varInfo, if the encoding parameter is in varInfo
    then encode text values using the dictImputeKeyException function
    '''
    resultDF = dataDF.copy()
    variables = varInfo['variables']
    for var in variables:
        if variables[var] is not None and 'encoding' in variables[var]:
            print '\tencoding text values...'
            try:
                mask_var = (resultDF['Variable Name'] == var)
                resultDF.loc[mask_var, 'Value'] = resultDF.loc[mask_var, 'Value'].apply(\
                    lambda x: variables[var]['encoding'][x])

            except KeyError as err:
                err.message = \
                    err.message + '\nError in vppreprocess.encode_text_values_by_variable()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' a value in the \'Value\' column of the data frame that' +\
                    ' does not have a mapping defined in the encoding.\n' + \
                    ' The values in the mapping are:\n\t' + \
                    ', '.join(variables[var]['encoding'].keys()) +\
                    '\nand the values you tried to map are:\n\t' + \
                    ', '.join(resultDF.loc[mask_var, 'Value'].unique())
                raise ValueError(err.message)
            except:
                print 'SOMETHING WAS WRONG WITH THE %s ENCODING: %s' \
                    % (var, variables[var]['encoding'])
    return resultDF

def convert_weird_numeric_by_variable(dataDF, varInfo):
    '''
    For each variable in varInfo, if the variable is a numeric variable
    (according to is_numeric_variable(varInfo, var)), then
    remove the following characters from dataDF['Value']:
        > < +
    '''
    for var in varInfo:
        if vppreprocess.is_numeric_variable(varInfo, var):
            mask_var                  = dataDF['Variable Name'] == var
            dataDF.loc[mask_var, 'Value'] = \
                dataDF.loc[mask_var, 'Value'].replace('>|<|\+', '', regex=True)
    return(dataDF)

def clip_values_by_variable(dataDF, varInfo):
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
                    err.message + '\nError in vppreprocess.clip_values()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' values in the \'Value\' column of the data frame that' +\
                    ' could not be cast to float.'
                raise ValueError(err.message)
    return dataDF

def age_normalize_by_variable(dataDF, encinfo, settings):
    '''
    For each variable in varInfo...
    '''
    birthdate = '2015-01-01 00:00:00'  #Valid only for Dataset 2!
    resultDF = dataDF.copy()

    for var in settings['variables'].keys():
        # Check for age-dependence flag
        # If age-dependent
        #     Compute age group, according the scheme found in varInfo
        #     Get parameters appropriate to age
        # Apply the formula
        mask_var = (resultDF['Variable Name'] == var)
        try:
            resultDF.ix[mask_var, 'Value'] = resultDF.ix[mask_var, 'Value'].astype(float)
        except ValueError as err:
                err.message = \
                    err.message + '\nError in ' +\
                    'vppreprocess.age_normalize_by_variable()' +\
                    ' while processing the ' + '\'Value\' column, for' +\
                    ' \'Variable Name\'==\'' + var + '\'.\nThere may be' +\
                    ' values in the \'Value\' column of the data frame that' +\
                    ' could not be cast to float.'
                raise ValueError(err.message)
        if settings['variables'][var]['age_dependent']:
            merged = resultDF.ix[mask_var,:].merge(encinfo, how='left', on='patient_id_encounter')
            merged['age_days'] = \
                (np.array(merged['Episode Start Timestamp'].values,
                dtype="datetime64[s]") -\
                np.datetime64(birthdate, 's') ).astype(int) / \
                86400.0

            # Get age group cutoffs and labels, sorted by cutoff
            sorted_age_groups = sorted(settings['age_groups'].items(),
                                        key=operator.itemgetter(1))
            labels = [x[0] for x in sorted_age_groups]
            cutoffs = [365*x[1] for x in sorted_age_groups] + [10**6]
            merged['age_group'] = pd.cut(merged['age_days'],
                                            bins =  cutoffs,
                                            labels = labels )

            # It would be more readable to groupby here, but I haven't figured out the details
            for age_gp in settings['age_groups'].keys():
                mask_age = merged['age_group']==age_gp
                if (np.any(mask_age)):
                    params = settings['variables'][var][age_gp]
                    med = params['median']
                    halfIQR = 0.5 * (params['quartile_3'] - params['quartile_1'])
                    if halfIQR == 0:
                        halfIQR = 1
                    age_values = merged.ix[mask_age,'Value'].values
                    merged.ix[mask_age,'Value'] = (age_values - med)/halfIQR
                    resultDF.ix[mask_var,'Value'] = merged['Value'].values
        else:
            params = settings['variables'][var]
            med = params['median']
            halfIQR = 0.5 * (params['quartile_3'] - params['quartile_1'])
            values = resultDF.ix[mask_var,'Value'].values
            resultDF.ix[mask_var,'Value'] = (values - med)/halfIQR
    resultDF['Value'] = resultDF['Value'].astype(str)
    return(resultDF)

def _DictImputeKeyException(x, dictionary):
    try:
        return dictionary[x]
    except KeyError:
        return x
