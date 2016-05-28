#!/usr/bin/env python

import sys
import os
import csv
import preprocessing
import pandas as pd

# Fetch command line arguments
args = sys.argv
data_dir   = args[1]
output_dir = args[2]

input_file  = 'timelines.csv'
output_file = 'timelines_clean.csv'

data_path = os.path.join(data_dir, input_file)
df = read_csv(data_path)

settings = preprocessing.load_settings()

df_clean = preprocessing.remove_nonnumeric(df)
df_clean = preprocessing.remove_extreme_by_variable(df_clean, settings['data'])

df_clean.to_csv(os.path.join(output_dir, output_file), index = False)
