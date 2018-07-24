import re
import os

import pandas as pd
import numpy as np

def load_data():
    files = os.listdir('./csvs/unclean_scraped_data/')
    dfs = []
    for i, csv in enumerate(files):
        exec(f'df{i} = pd.read_csv(\'./csvs/unclean_scraped_data/{csv}\')')
        exec(f'dfs.append(df{i})')
    
    return pd.concat(dfs)
    
master_df = load_data()

master_df.drop('Unnamed: 0',axis=1,inplace=True)
master_df.drop_duplicates(inplace=True)
master_df = pd.DataFrame(master_df[master_df.Salary.isnull() == False])

def remove_chars(data):
    '''Remove remaining HTML and other characters'''
    
    data['Company'].replace(to_replace='\n',
                           value='',
                           inplace=True, 
                           regex=True)

    data['Job Title'].replace(to_replace=['<b>','</b>'], 
                              value='',
                              inplace=True, 
                              regex=True) #Remove useless characters

    # More characters to remove
    data['Search Term'].replace(to_replace='\+', value = ' ', inplace=True, regex=True)
    data['Search Term'].replace(to_replace='\%2C', value = ',', inplace=True, regex=True)
    
    # Removing all characters between and including < >
    data['Location'].replace(to_replace='<.*?>',
                             value = '', 
                             inplace=True, 
                             regex=True)
    
    data = data[data['Salary'].str.contains('hour',case=False) == False]
    data = data[data['Salary'].str.contains('month',case=False) == False]
    
    
    # Take dollar signs out 
    data['Salary'].replace(to_replace=['\$',',',' a year'], 
                           value='', 
                           inplace=True,
                           regex=True)
    
    return data

master_df = remove_chars(master_df)

def split_func_lower(val):
    return val.split('-')[0]

def split_func_upper(val):
    val.split('-')
    try:
        return val.split('-')[1]
    except:
        return val.split('-')[0]
    
master_df['lower_sal_val'] = master_df['Salary'].apply(split_func_lower)
master_df['upper_sal_val'] = master_df['Salary'].apply(split_func_upper)

master_df['lower_sal_val'].replace(to_replace=' ', 
                                   value='', 
                                   inplace=True,
                                   regex=True)
master_df['upper_sal_val'].replace(to_replace=' ',
                                   value='', 
                                   inplace=True,
                                   regex=True)
    
master_df[['lower_sal_val','upper_sal_val']] = \
master_df[['lower_sal_val','upper_sal_val']].astype(int)

master_df['mean salary'] = 0.5*master_df['lower_sal_val'] + 0.5*master_df['upper_sal_val']

# Creating state col; no need to be super granular about locations.
master_df['state'] = master_df['Location'].str.findall('[A-Z]{2}')
master_df['state'] = master_df['state'].astype(str)
master_df['state'].replace(to_replace=['\[','\]'], value='',inplace=True,regex=True)


def percentile_cols(data):
    '''Create target cols for classification'''
    
    def above_percentile(val):
        '''Function to return median salary boolean'''
        if val > np.percentile(master_df['mean salary'],q=q):
            return True
        else:
            return False
    
    qs = [50, 60, 70, 75, 90]
    
    for q in qs:
        if q == 50:
            exec(f'data[\'median_bool\'] = data[\'mean salary\'].apply(above_percentile)')
        else:
            exec(f'data[\'{q}_perc_bool\'] = data[\'mean salary\'].apply(above_percentile)')
            
    return data

master_df = percentile_cols(master_df)

master_df.to_csv('./csvs/cleaned_data/clean_data.csv', index=False)