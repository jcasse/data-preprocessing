#!/usr/bin/env python

# Import libraries
import sys
import os
import vppreprocess
import pandas as pd
import numpy as np
import datetime
import yaml

# Fetch command line arguments
args = sys.argv
input_dir  = args[1]
output_dir = args[2]

extracttime = lambda x: str(datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").time())

def add_time_of_day_of_admission(encounterinfoDF):
    ret = encounterinfoDF.copy()
    ret['Time of Day of Admission'] = ret['Episode Start Timestamp'].apply(extracttime)
    return ret

def hms_to_seconds(hms):
    h, m, s = [int(i) for i in hms.split(':')]
    return str(3600 * h + 60 * m + s)

def to_seconds(df, colname):
    ret = df.copy()
    ret[colname] = ret[colname].apply(lambda x: hms_to_seconds(x))
    return ret

def timestamp_to_epoch(timestamp):
    return str(int((datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") - datetime.datetime(1970,1,1)).total_seconds()))

def to_epoch_time(df, colname):
    ret = df.copy()
    ret[colname] = ret[colname].apply(lambda x: timestamp_to_epoch(x))
    return ret

def normalize_epoch_times(dataDF, encinfoDF, timecolname):
    '''
    Expects timestamps in epoch time.
    '''
    joincolname = 'patient_id_encounter'
    basecolname = 'Episode Start Timestamp'
    rightDF = encinfoDF[[joincolname, basecolname]]
    ret = dataDF.merge(rightDF, how = 'left')
    ret[timecolname] = ret[timecolname].astype('int')
    ret[basecolname] = ret[basecolname].astype('int')
    ret[timecolname] = ret[timecolname] - ret[basecolname]
    ret[timecolname] = ret[timecolname].astype('str')
    del ret[basecolname]
    return ret

def remove_encounters_not_in_encinfo(df, encinfoDF):
    joincolname = 'patient_id_encounter'
    ret = df.merge(encinfoDF[[joincolname]], how = 'inner', on = joincolname)
    return ret

def remove_rows_with_empty_strings(df):
    ret = df.copy()
    # find rows wich have empty strings
    rows = np.where(ret.applymap(lambda x: x == ''))[0]
    # remove rows
    ret = ret.drop(ret.index[rows])
    return ret

def select_within_time_interval(df, timecolname, varInfo):
    '''
    Keep rows with time >= interval[0] and time < interval[1].
    Time specified in epoch time.
    '''
    interval = varInfo['time_interval']
    ret = df.copy()
    ret[timecolname] = ret[timecolname].astype('int')
    ret = ret[ret[timecolname] >= interval[0]]
    ret = ret[ret[timecolname] <  interval[1]]
    ret[timecolname] = ret[timecolname].astype('str')
    return ret

def test_select_within_time_interval():
    varInfoString = '''
        time_interval: [2, 4]
    '''
    settings = yaml.load(varInfoString)
    testDF = pd.DataFrame({'eid' : ['1', '2', '3', '4'],
                           'val' : ['1.0', '2.0', '3.0', '4.0'],
                           'End Time' : ['1', '2', '3', '4']
                            })
    testDF = testDF[['eid', 'val', 'End Time']] # arrange columns
    expectedDF = testDF.iloc[[1, 2]] # select rows with index 1 and 2
    resultDF = select_within_time_interval(testDF, 'End Time', settings)
    assert resultDF.equals(expectedDF)


def preprocess_data_file(filename, encinfoDf, settings):
    # Get data
    df = vppreprocess.read_data(os.path.join(input_dir, filename))

    # Perform pre-processing tasks
    df = vppreprocess.remove_episodes(df, settings)
    df = vppreprocess.remove_vars(df, settings)
    df = vppreprocess.remove_unmapped_text_value_by_variable(df, settings)
    df = vppreprocess.encode_text_values_by_variable(df, settings)
    df = vppreprocess.remove_nonnumeric(df)
    df = remove_encounters_not_in_encinfo(df, encinfoDF)
    #df = vppreprocess.age_normalize_by_variable(df, encinfoDF, settings)
    # doesn;t work with interventions that have both start and end time
    if 'Start Time' in df.columns:
        del df['End Time']
        df = to_epoch_time(df, 'Start Time')
        df = normalize_epoch_times(df, encinfoDF, 'Start Time')
        df = select_within_time_interval(df, 'Start Time', settings)
    else:
        #df = vppreprocess.remove_nondatetime(df, 'End Time')
        df = to_epoch_time(df, 'End Time')
        df = normalize_epoch_times(df, encinfoDF, 'End Time')
        df = select_within_time_interval(df, 'End Time', settings)
    df = vppreprocess.select_cols(df, settings)
    df = vppreprocess.rename_cols(df, settings)
    return df

def write_df_to_file(filename, output_dir, df):
    df.to_csv(os.path.join(output_dir, filename), index = False)

###############################################################################

# Load data specifications
settings = vppreprocess.load_settings('preprocessing_juan.yaml')

# Encounter Info
data_file = 'all_encounterinfo.csv'
encinfoDF = vppreprocess.read_data(os.path.join(input_dir, data_file))
encinfoDF = vppreprocess.remove_episodes(encinfoDF, settings)
encinfoDF = add_time_of_day_of_admission(encinfoDF)
encinfoDF = to_seconds(encinfoDF, 'Time of Day of Admission')
encinfoDF = to_epoch_time(encinfoDF, 'Episode Start Timestamp')
encinfoDF = vppreprocess.select_cols(encinfoDF, settings)
encinfoDF = remove_rows_with_empty_strings(encinfoDF)

# Events Data
#files = [
#    'all_vitalsigns.csv',
#    'all_labs.csv',
#    'all_interventions.csv'
#]
#for data_file in files:
#
#    # Get data
#    df = vppreprocess.read_data(os.path.join(input_dir, data_file))
#
#    # Perform pre-processing tasks
#    df = vppreprocess.remove_episodes(df, settings)
#    df = vppreprocess.remove_vars(df, settings)
#    df = vppreprocess.remove_unmapped_text_value_by_variable(df, settings)
#    df = vppreprocess.encode_text_values_by_variable(df, settings)
#    df = vppreprocess.remove_nonnumeric(df)
#    #df = vppreprocess.age_normalize_by_variable(df, encinfoDF, settings)
#    if 'Start Time' in df.columns:
#        del df['End Time']
#        df = to_epoch_time(df, 'Start Time')
#        df = normalize_epoch_times(df, encinfoDF, 'Start Time')
#    else:
#        #df = vppreprocess.remove_nondatetime(df, 'End Time')
#        df = to_epoch_time(df, 'End Time')
#        df = normalize_epoch_times(df, encinfoDF, 'End Time')
#    df = vppreprocess.select_cols(df, settings)
#
#    # Write output to file
#    df = vppreprocess.rename_cols(df, settings)
#    df.to_csv(os.path.join(output_dir, data_file), index = False)

#data_file = 'all_encounterinfo.csv'
#encinfoDF.to_csv(os.path.join(output_dir, data_file), index = False)

# Events Data
vitals = preprocess_data_file('all_vitalsigns.csv', encinfoDF, settings)
labs = preprocess_data_file('all_labs.csv', encinfoDF, settings)
inter = preprocess_data_file('all_interventions.csv', encinfoDF, settings)

# select and rename encinfo columns
encinfo = encinfoDF[['patient_id_encounter', 'Pre ICU CPR', 'Time of Day of Admission']]
encinfo = vppreprocess.rename_cols(encinfo, settings)

write_df_to_file('all_encounterinfo.csv', output_dir, encinfo)
write_df_to_file('all_vitalsigns.csv', output_dir, vitals)
write_df_to_file('all_labs.csv', output_dir, labs)
write_df_to_file('all_interventions.csv', output_dir, inter)
