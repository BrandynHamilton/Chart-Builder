import pandas as pd
import datetime as dt 
import plotly.colors as pc
import random
from IPython.display import Image, display
import os
import matplotlib.cm as cm
from matplotlib.colors import to_hex
import colorcet as cc
import json
import numpy as np


def dynamic_parameters(df, num_col='market_cap', scale=100, use_log_scale=False):
    max_value = df[num_col].max()
    min_value = df[num_col].min()

    # Apply logarithmic scaling if enabled
    if use_log_scale:
        df[num_col] = df[num_col].apply(lambda x: np.log1p(x))  # log1p to handle zeros safely
        max_value = df[num_col].max()
        min_value = df[num_col].min()

    # Compute dynamic marker_scale
    dynamic_marker_scale = max_value / scale  # Adjust divisor as needed

    return {
        'dynamic_marker_scale': dynamic_marker_scale,
    }

def calculate_marker_size(value, scaling_factor, max_size=210, min_size=8):
    size = min(value / scaling_factor, max_size)  # Cap the size
    size = max(size, min_size)  # Ensure a minimum size
    return size

def top_other_by_col_bubble(df, sort_col, sum_col, num=10, latest=True, groupby_color=None):
    print("\n=== Initial DataFrame ===")
    print(df)

    # Determine the columns to group by
    group_cols = [sort_col]
    if 'id' in df.columns:
        group_cols.append('id')
    if groupby_color and groupby_color not in group_cols:
        group_cols.append(groupby_color)
    if 'category' in df.columns and 'category' not in group_cols:
        group_cols.append('category')

    # Ensure group_cols contains unique values while preserving order
    group_cols = list(dict.fromkeys(group_cols))

    print("\n=== Grouping Columns ===")
    print(group_cols)

    # Aggregate the sum by sort_col for the entire DataFrame
    total_sum_by_group = df.groupby(sort_col)[sum_col].sum()
    print("\n=== Total Sum by Group ===")
    print(total_sum_by_group)

    # Handle top N filtering with 'latest' option
    if latest:
        recent = (
            df.groupby(group_cols)
            .tail(1)
            .sort_values(by=sum_col, ascending=False)
            .head(num)
        )
        recent_keys = recent[group_cols].drop_duplicates()
        print("\n=== Recent Top N (Latest) Keys ===")
        print(recent_keys)

        filtered_df = df.merge(recent_keys, on=group_cols)
    else:
        top = df.groupby(group_cols)[sum_col].sum()
        top_n = top.nlargest(num).reset_index()[group_cols]
        print("\n=== Top N (Non-Latest) Keys ===")
        print(top_n)

        filtered_df = df.merge(top_n, on=group_cols)

    print("\n=== Filtered Top N DataFrame ===")
    print(filtered_df)

    # Sum the values for the top N entries
    top_sum_by_group = filtered_df.groupby(sort_col)[sum_col].sum()
    print("\n=== Top N Sum by Group ===")
    print(top_sum_by_group)

    print(f'total sum: {total_sum_by_group}')

    # Calculate the 'Other' value by subtracting top_sum_by_group from total_sum_by_group
    other_value = (total_sum_by_group.sum() - top_sum_by_group.sum())
    print(f'other_value: {other_value}')
    other_sum_by_group = pd.DataFrame({
        sort_col: ['other'],
        sum_col: [other_value]
    })

    print(f'other_sum_by_group: {other_sum_by_group}')

    # Rename sum_col to match the aggregated column name
    # other_sum_by_group.rename(columns={sum_col: 'other_sum'}, inplace=True)
    # other_sum_by_group = other_sum_by_group.rename(columns={'other_sum': sum_col})
    print("\n=== Other Values Grouped DataFrame ===")
    other_sum_by_group = other_sum_by_group.groupby(sort_col)[[sum_col]].sum()
    print(other_sum_by_group)

    # Create 'Other' DataFrame
    other_df = other_sum_by_group.copy()
    if 'id' in df.columns:
        other_df['id'] = 'other'
    if groupby_color not in df.columns:
        other_df[groupby_color] = 'other'
    if 'symbol' in df.columns:
        other_df['symbol'] = 'other'
    if 'category' in df.columns:
        other_df['category'] = 'other'
    if 'network' not in other_df.columns:
        other_df['network'] = 'other'
    
    # other_df = other_df.reset_index()

    print("\n=== Other DataFrame ===")
    print(other_df)

    if other_value > 0:
    # Combine filtered_df and other_df
        combined = pd.concat([filtered_df, other_df], ignore_index=True)
    else:
        combined = filtered_df.copy()
    combined.sort_index(inplace=True)

    print("\n=== Combined DataFrame ===")
    print(combined)

    return combined



def top_by_col_bubble(df, sort_col, sum_col, num=10, latest=True, groupby_color=None):
    print("\n=== Initial DataFrame ===")
    print(df)

    # Determine the columns to group by
    group_cols = [sort_col]
    if 'id' in df.columns:
        group_cols.append('id')
    if groupby_color:
        group_cols.append(groupby_color)

    print("\n=== Grouping Columns ===")
    # Ensure group_cols contains unique values while preserving order
    group_cols = list(dict.fromkeys(group_cols))

    print(group_cols)

    # Handle top N filtering with 'latest' option
    if latest:
        recent = (
            df.groupby(group_cols)
            .tail(1)
            .sort_values(by=sum_col, ascending=False)
            .head(num)
        )
        recent_keys = recent[group_cols].drop_duplicates()
        print("\n=== Recent Top N (Latest) Keys ===")
        print(recent_keys)

        filtered_df = df.merge(recent_keys, on=group_cols)
    else:
        top = df.groupby(group_cols)[sum_col].sum()
        top_n = top.nlargest(num).reset_index()[group_cols]
        print("\n=== Top N (Non-Latest) Keys ===")
        print(top_n)

        filtered_df = df.merge(top_n, on=group_cols)

    print("\n=== Filtered Top N DataFrame ===")
    print(filtered_df)

    filtered_df.sort_index(inplace=True)

    print("\n=== filtered_df DataFrame ===")
    print(filtered_df)

    return filtered_df

def clean_values(x, decimals=True, decimal_places=1):
    if isinstance(x, pd.Series):
        return x.apply(clean_values, decimals=decimals, decimal_places=decimal_places)
    
    if x == 0:
        return '0'

    if decimals == True:
        if abs(x) < 1:  # Handle numbers between -1 and 1 first
            print(f'x < 1:{x}')
            return f'{x:.2f}'  # Keep small values with two decimal points
        elif x >= 1e12 or x <= -1e12:
            print(f'x:{x}T')
            return f'{x / 1e12:.{decimal_places}f}T'  # Trillion
        elif x >= 1e9 or x <= -1e9:
            print(f'x:{x}B')
            return f'{x / 1e9:.{decimal_places}f}B'  # Billion
        elif x >= 1e6 or x <= -1e6:
            print(f'x:{x}M')
            return f'{x / 1e6:.{decimal_places}f}M'  # Million
        elif x >= 1e3 or x <= -1e3:
            print(f'x:{x}k')
            return f'{x / 1e3:.{decimal_places}f}k'  # Thousand
        elif x >= 1e2 or x <= -1e2:
            print(f'x:{x}')
            return f'{x:.{decimal_places}f}'  # Show as is for hundreds
        elif x >= 1 or x <= -1:
            print(f'x:{x}')
            return f'{x:.{decimal_places}f}'  # Show whole numbers for numbers between 1 and 100
        else:
            print(f'x:{x}')
            return f'{x:.{decimal_places}f}'  # Handle smaller numbers
    
    else:
        if abs(x) < 1:  # Handle numbers between -1 and 1 first
            return f'{x:.2f}'  # Keep small values with two decimal points
        elif x >= 1e12 or x <= -1e12:
            return f'{x / 1e12:.0f}t'  # Trillion
        elif x >= 1e9 or x <= -1e9:
            return f'{x / 1e9:.0f}b'  # Billion
        elif x >= 1e6 or x <= -1e6:
            return f'{x / 1e6:.0f}m'  # Million
        elif x >= 1e3 or x <= -1e3:
            return f'{x / 1e3:.0f}k'  # Thousand
        elif x >= 1e2 or x <= -1e2:
            return f'{x:.0f}'  # Show as is for hundreds
        elif x >= 1 or x <= -1:
            return f'{x:.0f}'  # Show as is for numbers between 1 and 100
        else:
            return f'{x:.0f}'  # Handle smaller numbers

def create_df(columns, data):
    df = pd.DataFrame(data, columns=columns)
    return df

def clean_values_dollars(x):
    if isinstance(x, pd.Series):
        return x.apply(clean_values)

    if x >= 1e9 or x <= -1e9:
        return f'-${abs(x / 1e9):,.1f}B' if x < 0 else f'${x / 1e9:,.1f}B'  # Billion
    elif x >= 1e6 or x <= -1e6:
        return f'-${abs(x / 1e6):,.1f}M' if x < 0 else f'${x / 1e6:,.1f}M'  # Million
    elif x >= 1e3 or x <= -1e3:
        return f'-${abs(x / 1e3):,.0f}k' if x < 0 else f'${x / 1e3:,.0f}K'  # Thousand
    elif x >= 1e2 or x <= -1e2:
        return f'-${abs(x):,.0f}' if x < 0 else f'${x:,.0f}'  # Show as is for hundreds
    elif x >= 1 or x <= -1:
        return f'-${abs(x):,.2f}' if x < 0 else f'${x:,.2f}'  # Show two decimals for numbers between 1 and 100
    else:
        return f'-${abs(x):,.2g}' if x < 0 else f'${x:,.2g}'  # Scientific notation for small numbers or handle negatives appropriately

    
def to_df(file, delimiter=','):
    df_path = f'{file}'
    
    try:
        # Check if the file is an Excel file
        if df_path.endswith('.xlsx') or df_path.endswith('.xls'):
            df = pd.read_excel(df_path)
        else:
            # Assume it's a CSV file if it doesn't have an Excel extension
            df = pd.read_csv(df_path, delimiter=delimiter)
        
        print(df.head(), "\n", df.tail())
        return df
    
    except FileNotFoundError:
        print(f"Error: File {df_path} not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: File {df_path} is empty.")
    except UnicodeDecodeError:
        print(f"Error: {df_path} contains invalid encoding.")
    except Exception as e:
        print(f"Error loading {df_path}: {e}")

def to_time(df, time_col=None, dayfirst=False, convert_to_datetime=True, drop_mid_timefreq=True):
    import pandas as pd

    time_cols = ['date', 'dt', 'hour', 'time', 'day', 'month', 'year', 
                 'week', 'timestamp', 'date(utc)', 'block_timestamp', 
                 'ds', 'period', 'date_time', 'trunc_date', 'quarter', 'block_time',
                 'block_date']
    
    # Append the custom time column if provided
    time_cols.append(time_col.lower() if time_col is not None else None)
    
    print(f'{time_col}')
    print(f'{time_cols}')

    time_freq = 'd'  # Default time frequency
    time_col_found = False  # Flag to check if we have found a time column

    for col in df.columns:
        print(f'col: {col}')

        if drop_mid_timefreq:
            # Check for specific time columns to set time_freq
            if col.lower() in ['week', 'month', 'quarter']:
                print(f'time_freq: {col}')
                time_freq = {'week': 'w', 'month': 'm', 'quarter': 'q'}[col.lower()]
                time_col_found = True  # Indicate we found a time column

        if col.lower() in time_cols and col.lower() != 'timestamp':
            if col.lower() == 'year':  # Handle 'year' column explicitly
                print(f"Converting 'year' column to datetime")
                df[col] = pd.to_datetime(df[col].astype(str), format='%Y')  # Convert to datetime
                df[col] = df[col].dt.year  # Keep only the year as integer
                df = df.set_index(col)  # Set the 'year' column as the index
            elif convert_to_datetime:
                print(f'convert col to dt: {col}')
                if dayfirst:
                    df[col] = pd.to_datetime(df[col], dayfirst=True).dt.tz_localize(None)  # Remove timezone
                else:
                    df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)  # Remove timezone
                df = df.set_index(col)  # Set the identified column as the index
            else:
                print(f'Column {col} will not be converted to datetime.')
                df = df.set_index(col)
        
        elif col.lower() == 'timestamp':
            df[col] = pd.to_datetime(df[col], unit='ms').dt.tz_localize(None)  # Remove timezone
            df = df.set_index(col)  # Set the timestamp column as the index

    if not time_col_found:  # If no specific time column was found, default to daily
        print('No specific time column found. Defaulting to daily frequency.')

    print(df.index)
    print(f'time_freq: {time_freq}')
    return df, time_freq
            
def clean_dates(df, time_freq):
    print(f'time_freq:{time_freq}')
    # Assumes index is datetime
    today = dt.date.today()
    today = pd.to_datetime(today).tz_localize(None)  # Ensure today is timezone-naive
    print(f'today: {today}')

    # Get the latest timestamp in the DataFrame
    latest_date = df.index.max()
    print(f'latest_date:{latest_date}')

    if time_freq == 'w':
        # Check if the latest_date is in the current week
        if latest_date >= today - pd.to_timedelta(today.weekday(), unit='d'):
            df = df[df.index < (today - pd.to_timedelta(today.weekday(), unit='d'))]

    elif time_freq == 'm':
        # Check if the latest_date is in the current month
        if latest_date >= today.replace(day=1):
            df = df[df.index < today.replace(day=1)]

    elif time_freq == 'q':
        # Get the start of the current quarter
        current_quarter = (today.month - 1) // 3 + 1
        quarter_start = dt.date(today.year, (current_quarter - 1) * 3 + 1, 1)

        # Check if the latest_date is in the current quarter
        if latest_date >= quarter_start:
            df = df[df.index < quarter_start]

    else:
        # Default case for daily cleaning
        df = df[df.index < today]

    print(f'df index: {df.index}')
    df.sort_index(ascending=True, inplace=True)
    
    return df
   
    
def latest_values(series):
    # Get the last row (which is the latest due to the sorted index)
    l_date = series.index[-1]
    l_val = series.iloc[-1]
    
    # Format the values
    formatted_val = f"{l_val:,.0f}"
    formatted_date = l_date.strftime('%m-%d-%Y')
    print(f'latest date: {formatted_date}, last value: {formatted_val}')
    
    return formatted_val, formatted_date

def colors(shuffle=False):
    # Existing Plotly palettes
    color_palette = pc.qualitative.Plotly[::-1]
    distinct_palette = pc.qualitative.Dark24 + pc.qualitative.Set3
    
    # Add Matplotlib colors
    matplotlib_colors = [to_hex(cm.tab10(i)) for i in range(10)] + \
                        [to_hex(cm.Set1(i)) for i in range(9)]
    
    # Add Colorcet colors
    colorcet_colors = cc.palette['glasbey_dark'] + cc.palette['glasbey_light']

    # Combine all palettes
    lib_colors = distinct_palette + color_palette + matplotlib_colors + colorcet_colors

    if shuffle:
        random.shuffle(lib_colors)

    # print(f'Combined colors: {lib_colors} \nCombined colors length: {len(lib_colors)}')
    
    return lib_colors

def data_processing(path=None, file=None, time_col=None, dayfirst=False, turn_to_time=True, dropna=False, fillna=False, ffill=False, resample_freq=None,
                    delimiter=',', start_date=None, end_date=None, cols=None, dropna_col=False,
                    keepna=False, drop_duplicates=True, set_time_col=False,drop_mid_timefreq=True,agg_func='sum',
                    to_clean_dates=True,sort_col=None):
    print(f'turning to df')
    if path is None:
        path = f'../data/{file}'
    
    df = to_df(path, delimiter)  # Assuming to_df is defined elsewhere
    
    if drop_duplicates:
        print(f'Dropping Duplicates')
        df.drop_duplicates(inplace=True)

    print(f'turn to time: {turn_to_time}')
    print(f'set time col: {set_time_col}')

    # If turn_to_time is False, handle accordingly
    if not turn_to_time:
        if fillna:
            df = df.fillna(0)
        
        if dropna:
            print(f'NaN detected, Dropping NaN Values')
            df.dropna(inplace=True)
        elif dropna_col:
            print(f'NaN detected, Dropping NaN Values in specified column')
            df = df.dropna(axis=1)
        elif keepna:
            df = df.copy()

        # Set time column if required
        if set_time_col:
            df, time_freq = to_time(df=df, time_col=time_col, dayfirst=dayfirst,drop_mid_timefreq=drop_mid_timefreq, convert_to_datetime=False)

        # Select specified columns if provided
        if cols == 'All':
            cols = df.columns
        if cols is not None and len(cols) > 0:  # Check if cols is a list and not empty
            df = df[cols]

        return df

    print(f'turning to dt')
    
    # Handle NaN values before converting to datetime
    if df.isna().any().any():
        if dropna:
            print(f'NaN detected, Dropping NaN Values')
            df.dropna(inplace=True)
        elif fillna:
            print(f'NaN detected, Filling NaN w/ 0')
            df = df.fillna(0)
        elif dropna_col:
            print(f'NaN detected, Dropping NaN Values in specified column')
            df = df.dropna(axis=1)
        elif ffill:
            print(f'NaN detected, Filling NaN w/ Forward Fill')
            df = df.ffill()
        elif not keepna:
            print(f'NaN detected, requires manual cleaning')
            return df
    
    # Convert time columns to datetime if turn_to_time is True
    df, time_freq = to_time(df, time_col, dayfirst,drop_mid_timefreq=drop_mid_timefreq)

    # Select specified columns if provided
    if cols == 'All':
        cols = df.columns
    if cols is not None and len(cols) > 0:  # Check if cols is a list and not empty
        df = df[cols]

    # Filter by date range if specified
    if start_date is not None and end_date is not None:
        df = df[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))]
    elif start_date is not None:
        df = df[df.index >= pd.to_datetime(start_date)]
    elif end_date is not None:
        df = df[df.index <= pd.to_datetime(end_date)]

    # Resample the DataFrame if resample_freq is specified
    if resample_freq is not None:
        original_df = df.copy()
        print(f'resampling: {resample_freq}, how: {agg_func}')
        if resample_freq == 'Q':
            if agg_func == 'sum':
                df = df.resample(resample_freq).sum()
            elif agg_func == 'last':
                df = df.resample(resample_freq).last()
            df.index = df.index.to_period('Q').strftime('Q%q %y')
            print(df.index)
        else:
            if agg_func == 'sum':
                df = df.resample(resample_freq).sum()
            elif agg_func == 'last':
                df = df.resample(resample_freq).last()
            print(df.index)
        print(f'df after resample: {df}')
        
        if sort_col != None:
            print(f'sort_col: {sort_col}')
            df = df.drop(columns=sort_col).merge(original_df[sort_col], left_index=True, right_index=True, how='inner')
            print(f'df after merge: {df}')
    if to_clean_dates:
        print(f'cleaning dates')
        df = clean_dates(df,time_freq)  # Assuming clean_dates is defined elsewhere
    
    print(df.columns)

    return df

def rank_by_col(df, sort_col, num_col, descending=True, cumulative_sort=False, colors=None):
    print(f"df @ rank_by_col: {df}")

    df.sort_index(inplace=True)

    # Generate cumulative sort order
    if cumulative_sort:
        # breakpoint()
        # Calculate cumulative sum and sort by `num_col`
        print(f'df: {df}')
        cumulative_sorted_list = (
            df.groupby(sort_col)[num_col]
            .sum()
            .sort_values(ascending=not descending)
            .index
            .tolist()
        )
    else:
        cumulative_sorted_list = []

    # Generate plot/legend order based on the latest values
    all_signers = df[sort_col].unique()
    last_day = df.index.max()
    last_records = df.groupby(sort_col).tail(1)
    last_day_records = last_records[last_records.index == last_day]

    missing_signers = set(all_signers) - set(last_day_records[sort_col])
    missing_df = pd.DataFrame({
        sort_col: list(missing_signers),
        num_col: 0
    })
    print(f"Available columns in df: {df.columns}")
    print(f"sort_col: {sort_col}")
    print(f"num_col: {num_col}")

    combined_df = pd.concat([last_day_records.reset_index(drop=True), missing_df.reset_index(drop=True)])
    combined_df = combined_df.sort_values(by=num_col, ascending=not descending).drop_duplicates()

    # Generate the sorted list for plotting
    latest_sorted_list = combined_df.reset_index()[sort_col].values.tolist()

    # Generate the color map based on cumulative or latest sort
    if colors:
        if cumulative_sort:
            # Colors based on cumulative rank
            if descending:
                color_map = {val: colors[idx % len(colors)] for idx, val in enumerate(cumulative_sorted_list)}
            else:
                color_map = {val: colors[idx % len(colors)] for idx, val in enumerate(reversed(cumulative_sorted_list))}
        else:
            # Colors based on latest value rank
            if descending:
                color_map = {val: colors[idx % len(colors)] for idx, val in enumerate(latest_sorted_list)}
            else:
                color_map = {val: colors[idx % len(colors)] for idx, val in enumerate(reversed(latest_sorted_list))}
    else:
        color_map = {}

    return latest_sorted_list, color_map

# def rank_by_columns(df, cumulative=False, descending=True):
#     """
#     Rank columns in a DataFrame based on the last row or cumulative sum of values.
    
#     Parameters:
#     - df (pd.DataFrame): Input DataFrame
#     - cumulative (bool): If True, ranks by the cumulative sum of each column.
#     - descending (bool): Sort order; True for descending, False for ascending.

#     Returns:
#     - list: Ordered list of column names based on ranking.
#     """
#     if cumulative:
#         # Sum all values in each column and sort by the cumulative total
#         sort_list = df.sum().sort_values(ascending=not descending)
#     else:
#         # Sort by the last row values
#         sort_list = df.iloc[-1].sort_values(ascending=not descending)
    
#     print(f'Sorted values for ranking: {sort_list}')
    
#     # Return the sorted column names
#     if descending:
#         return sort_list.index.tolist()[:-1] + [sort_list.index[-1]]  # largest last
#     else:
#         return [sort_list.index[0]] + sort_list.index.tolist()[1:]  # largest first

def rank_by_columns(df, cumulative=False, descending=True):
    """
    Rank columns in a DataFrame based on the last row or cumulative sum of values.

    Parameters:
    - df (pd.DataFrame): Input DataFrame
    - cumulative (bool): If True, ranks by the cumulative sum of each column.
    - descending (bool): Sort order; True for descending, False for ascending.

    Returns:
    - pd.Index: Ordered column names based on ranking.
    """
    if cumulative:
        # Rank by cumulative sum
        sort_list = df.select_dtypes(include=['number']).sum().sort_values(ascending=not descending)
    else:
        # Rank by the latest row
        sort_list = df.iloc[-1].sort_values(ascending=not descending)

    print(f"Ranked columns: {sort_list}")
    return sort_list.index

def top_ten_with_others(df, rank_col, sort_col, top_n=9):

    if rank_col is None and sort_col is None:
        top = df.iloc[-1].sort_values(ascending=False).head(top_n)
        top_df = df[top.index.to_list]
        
        other = df.loc[:, ~df.columns.isin(top.index)].sum(axis=1)
        other_df = other.to_frame('other')

        combined = pd.merge(top_df, other_df, left_index=True, right_index=True, how='inner')
        return combined
    else:
        # Sort the DataFrame by the specified column and take the top N rows
        top_df = df.sort_values(by=rank_col, ascending=False).head(top_n).reset_index()

        # Sum the rest of the rows to create an "Other" group
        other = df.sort_values(by=rank_col, ascending=False).iloc[top_n:][rank_col].sum()

        # Create a DataFrame for the "Other" group
        other_df = pd.DataFrame({sort_col: ["other"], rank_col: [other]})

        # Combine the top shows and the "Other" group
        combined_df = pd.concat([top_df, other_df], ignore_index=False)
        print(f'index: {combined_df}')

        # combined_df.drop_duplicates(inplace=True)
        return combined_df

def top_ten(df, rank_col,topn=5):
    top_df = df.sort_values(by=rank_col, ascending=False).head(topn)
    # top_df.drop_duplicates(inplace=True)
    return top_df

def ranked_cleaning(df, num_col, sort_col, descending=True,use_sort_list=True): 
    df_copy = df.copy()
    df_copy = df_copy[[sort_col, num_col]]
    print(f'df in ranked cleaning: {df_copy}')
    print(f'orig sort order: {df_copy[sort_col].unique()}')
    print(f'use_sort_list: {use_sort_list}')

    if use_sort_list==True:

        # Sort by the transaction number column based on the descending parameter
        df_copy.sort_values(by=num_col, inplace=True, ascending=not descending)  # Use `not descending` for the sort order
        sort_list = df_copy[sort_col].unique()
    else:
        #We keep original sort order
        sort_list = df_copy[sort_col].unique()
    df_copy.drop_duplicates(inplace=True)

    return df_copy, sort_list


# def to_percentage(df, sum_col, index_col):

#     df_copy = df.copy()

#     # Calculate total usd_revenue
#     total = df_copy[sum_col].sum()

#     # Add a new column for percentage
#     df_copy['percentage'] = (df_copy[sum_col] / total) * 100
#     df_copy['legend_label'] = df_copy.apply(lambda x: f"{x[index_col]} ({x['percentage']:.1f}%)", axis=1)
#     df_copy.set_index('legend_label', inplace=True)
#     df_copy.sort_values(by=sum_col, ascending=False, inplace=True)
#     df_copy.drop_duplicates(inplace=True)

#     return df_copy, total

def to_percentage(df, sum_col, index_col, percent=True):

    df_copy = df.copy()

    df_copy = df_copy.groupby(index_col)[sum_col].sum().reset_index()

    # Calculate total usd_revenue
    total = df[sum_col].sum()

    if percent:

        # Add a new column for percentage
        df_copy['percentage'] = (df_copy[sum_col] / total) * 100
        df_copy['legend_label'] = df_copy.apply(lambda x: f"{x[index_col]} ({x['percentage']:.1f}%)", axis=1)
        df_copy.set_index('legend_label', inplace=True)
    else:
        df_copy.set_index(index_col, inplace=True)
        print(f'df_copy: {df_copy}')
    
    df_copy.sort_values(by=sum_col, ascending=False, inplace=True)
    df_copy.drop_duplicates(inplace=True)

    return df_copy, total

def normalize_to_percent(df,num_col=None):
    print(f'num_col: {num_col}')

    if num_col == None:
    
        df_copy = df.copy()

        df_copy['total'] = df_copy.sum(axis=1)
        # Exclude the 'total_transactions' column from the percentage calculation
        chains_columns = df_copy.columns.difference(['total'])

        for col in chains_columns:
            df_copy[f'{col}_percentage'] = (df_copy[col] / df_copy['total']) * 100

        # Drop the 'total_transactions' column if you don't need it
        df_copy = df_copy.drop(columns=['total'])

        percent_cols = [col for col in df_copy.columns if '_percentage' in col]
        df_copy = df_copy[percent_cols]

        df_copy.columns = df_copy.columns.str.replace('_percentage', '', regex=False)

        print(f'percent_cols:{df_copy.columns}')
    else:
        df_copy = df.copy()
        total = df_copy.groupby(df_copy.index)[num_col].sum()
        total = total.to_frame(f'total_{num_col}')
        df_copy = df_copy.merge(total, left_index=True, right_index=True, how='inner')
        # Calculate percentage of daily active users for each app
        df_copy['percentage'] = (df_copy[num_col] / df_copy[f'total_{num_col}']) * 100

        # Drop the total_active_users column if no longer needed
        df_copy = df_copy.drop(columns=[f'total_{num_col}'])
        df_copy.drop(columns=num_col,inplace=True)

        df_copy.rename(columns={"percentage":num_col},inplace=True)

    df_copy.drop_duplicates(inplace=True)

    return df_copy

def top_by_col(df, sort_col, sum_col, num=10, latest=True):
    # Step 1: Group by 'make' and calculate the sum of 'mints_per_week'
    if latest==True:
        recent = df.groupby(sort_col).tail(1).sort_values(by=sum_col,ascending=False).head(num)[sort_col].values.tolist()
        filtered_df = df[df[sort_col].isin(recent)]

    else:
        top = df.groupby(sort_col)[sum_col].sum()

        # Step 2: Sort the makes by the sum of 'mints_per_week' in descending order and keep the top 10
        top_10 = top.nlargest(num).index

        # Step 3: Filter the original DataFrame to keep only rows with the top 10 makes
        filtered_df = df[df[sort_col].isin(top_10)]

        # Optionally, reset the index
        # filtered_df = filtered_df.reset_index()

    filtered_df.drop_duplicates(inplace=True)

    return filtered_df

# def top_other_by_col(df, sort_col, sum_col, num=10, latest=True):
#     # Step 1: Group by 'make' and calculate the sum of 'mints_per_week'
#     if latest==True:
#         recent = df.groupby(sort_col).tail(1).sort_values(by=sum_col,ascending=False).head(num)[sort_col].values.tolist()
#         filtered_df = df[df[sort_col].isin(recent)]

#         other = df[~df[sort_col].isin(recent)]
#         other_values = other.groupby(sort_col)[sum_col].sum()

#         other_df = pd.DataFrame({
#         sort_col: [f'other'] * len(other_values),
#         sum_col: other_values.values
#         })

#         combined = pd.concat([filtered_df,other_df], ignore_index=False)
#         print(F'combined: {combined}')
#         combined.sort_index(inplace=True)
#     else:
#         top = df.groupby(sort_col)[sum_col].sum()

#         # Step 2: Sort the makes by the sum of 'mints_per_week' in descending order and keep the top 10
#         top_10 = top.nlargest(num).index

#         # Step 3: Filter the original DataFrame to keep only rows with the top 10 makes
#         filtered_df = df[df[sort_col].isin(top_10)]

#         other = df[~df[sort_col].isin(recent)]
#         other_values = other.groupby(sort_col)[sum_col].sum()

#         other_df = pd.DataFrame({
#         sort_col: [f'other'] * len(other_values),
#         sum_col: other_values.values
#         })

#         combined = pd.concat([filtered_df,other_df], ignore_index=True)
#         combined.sort_index(inplace=True)

#         # Optionally, reset the index
#         # filtered_df = filtered_df.reset_index()

#     print(f'combined: {combined}')

#     # combined = combined.groupbby([combined.index,sort_col])[[sum_col]].sum().reset_index(drop=True)

#     # combined.drop_duplicates(inplace=True)

#     return combined

def top_other_by_col(df, sort_col, sum_col, num=10, latest=True):
    print(F'latest: {latest}')
    # Step 1: Group by 'make' and calculate the sum of 'mints_per_week'
    if latest==True:
        recent = df.groupby(sort_col).tail(1).sort_values(by=sum_col,ascending=False).head(num)[sort_col].values.tolist()
        filtered_df = df[df[sort_col].isin(recent)]

        other = df[~df[sort_col].isin(recent)][[sum_col]].drop_duplicates()
        other_df = other.groupby(other.index)[[sum_col]].sum()

        other_df[f'{sort_col}'] = 'other'

        combined = pd.concat([filtered_df,other_df], ignore_index=False)

        combined.sort_index(inplace=True)
    else:
        top = df.groupby(sort_col)[[sum_col]].sum().sort_values(by=sum_col,ascending=False).head(num).index

        # Step 3: Filter the original DataFrame to keep only rows with the top 10 makes
        filtered_df = df[df[sort_col].isin(top)]

        # other = df[~df[sort_col].isin(recent)]
        others = df[~df[sort_col].isin(top)][[sum_col]].drop_duplicates()
        others_values = others.groupby(others.index)[[sum_col]].sum()

        others_values[f'{sort_col}'] = 'other'

        filtered_df = filtered_df[[sort_col,sum_col]]

        combined = pd.concat([filtered_df,others_values]).sort_index().drop_duplicates()

    print(f'combined: {combined}')

    return combined

# For timeseries

def top_other_ts_by_col(df,num_col, sort_col, topn=9):
    list = rank_by_col(df=df,sort_col=sort_col,num_col=num_col)
    list = list[0]
    top_df = df[df[sort_col].isin(list[0:topn])]

    other = df[~df[sort_col].isin(list[0:topn])]
    # other_num = len(other.columns)
    other_values = other.groupby(other.index)[num_col].sum()
    other_df = pd.DataFrame({
        sort_col: [f'other'] * len(other_values),
        num_col: other_values.values
    }, index=other_values.index)

    combined = pd.concat([top_df,other_df], ignore_index=False)
    combined.sort_index(inplace=True)

    return combined

def top_other_ts_by_columns(df, topn=9, num_other = False):
    list = rank_by_columns(df)
    print(f'top {topn} cols: {list[0:topn]}')
    other_cols = [col for col in df.columns if col not in(list[0:topn])]
    print(f'other cols: {other_cols}')
    top = df[list[0:topn]]
    other_df = df[other_cols]
    other_df = other_df.sum(axis=1).to_frame('other')
    combined = pd.merge(top,other_df,left_index=True, right_index=True, how='inner')
    if num_other == True:
        combined.rename(columns={'other':f'others ({len(other_cols)})'},inplace=True)

    return combined

def top_ts_by_col(df,num_col, sort_col, topn=9):
    list = rank_by_col(df=df,sort_col=sort_col,num_col=num_col)
    list = list[0]
    print(f'list: {list}')
    top_df = df[df[sort_col].isin(list[0:topn])]

    return top_df

def top_ts_only_by_columns(df, topn=9):
    list = rank_by_columns(df)
    print(f'top {topn} cols: {list[0:topn]}')
    top = [col for col in df.columns if col in(list[0:topn])]
    df_new = df[top]

    return df_new

def clean_string(value, capwords, clean_words):
    # Replace underscores and convert to title case initially
    cleaned_value = value.replace('_', ' ').title()
    
    # Check for capitalization based on capwords
    for word in cleaned_value.split():
        if word.upper() in capwords:
            print(f"'{value}' matches capword. Keeping as uppercase: {word.upper()}")
            cleaned_value = cleaned_value.replace(word, word.upper())
        else:
            print(f"'{value}' does not match capword. Converting to title case: {word.title()}")

    # Replace words based on the clean_words mapping
    for old_word, new_word in clean_words.items():
        cleaned_value = cleaned_value.replace(old_word, new_word)

    print(f"Cleaned string: '{cleaned_value}'")
    return cleaned_value

def cleaning(df, cols_to_plot, bar_col, line_col, groupby, num_col, y1_list=None, y2_list=None, capwords=None, clean_words=None):
    # Ensure capwords is a list of uppercase words
    capwords = [word.upper() for word in (capwords or [])]
    print(f'capwords: {capwords}')

    print(f'y1_list: {y1_list} \ny2_list: {y2_list}')
    
    # Prepare the replacement mapping if clean_words is provided
    clean_words = clean_words or {}

    # Clean the DataFrame column names
    df.columns = [
        col.replace('_', ' ').title() if not any(word.upper() in capwords for word in col.replace('_', ' ').split())
        else col.replace('_', ' ').title()  # Replace underscores and convert to title case initially
        for col in df.columns
    ]

    # Update with the correct capitalization for capwords
    df.columns = [
        ' '.join(word.upper() if word.upper() in capwords else word for word in col.split())
        for col in df.columns
    ]

    # Replace words in the DataFrame based on the clean_words dictionary
    for old_word, new_word in clean_words.items():
        df = df.replace(old_word, new_word, regex=True)

    # Explicitly check if variables are None before cleaning
    cols_to_plot = [] if cols_to_plot is None else list(cols_to_plot)
    bar_col = [] if bar_col is None else list(bar_col)
    line_col = [] if line_col is None else list(line_col)

    # Clean the array values using the clean_string helper function
    cols_to_plot = [clean_string(col, capwords, clean_words) for col in cols_to_plot]
    bar_col = [clean_string(col, capwords, clean_words) for col in bar_col]
    line_col = [clean_string(col, capwords, clean_words) for col in line_col]

    # Clean y1_list and y2_list only if they are not None
    if y1_list is not None:
        y1_list = [clean_string(col, capwords, clean_words) for col in y1_list]
    
    if y2_list is not None:
        y2_list = [clean_string(col, capwords, clean_words) for col in y2_list]

    # Clean the groupby column (single string)
    if groupby:
        groupby_cleaned = clean_string(groupby, capwords, clean_words)
        print(f"Cleaned groupby: {groupby_cleaned}")
    else:
        groupby_cleaned = groupby

    # Clean the num_col column (single string)
    if num_col:
        num_col_cleaned = clean_string(num_col, capwords, clean_words)
        print(f"Cleaned num_col: {num_col_cleaned}")
    else:
        num_col_cleaned = num_col

    # Print cleaned columns for verification
    print("Cleaned DataFrame columns:", df.columns.tolist())
    print("Cleaned cols_to_plot:", cols_to_plot)
    print("Cleaned bar_col:", bar_col)
    print("Cleaned line_col:", line_col)
    print("Cleaned y1_list:", y1_list)
    print("Cleaned y2_list:", y2_list)
    print("Cleaned groupby:", groupby_cleaned)
    print("Cleaned num_col:", num_col_cleaned)

    return df, cols_to_plot, bar_col, line_col, y1_list, y2_list, groupby_cleaned, num_col_cleaned

def cleaning_values(df):
    for col in df.columns:
        df[col] = (
            df[col]
            .str.replace('#DIV/0!', 'NaN', regex=False)  # Replace '#DIV/0!' with NaN
            .str.replace('%', '', regex=False)            # Remove the percent sign
            .str.replace(',', '', regex=False)            # Remove commas
            .str.replace('$', '', regex=False)            # Remove dollar signs
        )
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def get_submission_df(submissions_data, submission_num, submission_directory):
    # Get the submission data
    try:
        submission = submissions_data[submission_num]
    except IndexError:
        raise ValueError("Submission number is out of range.")

    # Initialize dictionaries to store DataFrames and images
    project = submission['project']
    data_struct = {}
    images = {}

    # Loop through CSVs and corresponding images
    for i in range(1, 4):  # Assuming 'csv_1', 'csv_2', 'csv_3' and 'image_1', 'image_2', 'image_3'
        csv_key = f'csv_{i}'
        img_key = f'image_{i}'

        # Load CSV or Excel based on the file extension
        csv_filename = submission['data'].get(csv_key)
        if csv_filename:
            csv_path = os.path.join(submission_directory, csv_filename)
            try:
                # Check if the file is an Excel file
                if csv_filename.endswith('.xlsx') or csv_filename.endswith('.xls'):
                    df = pd.read_excel(csv_path)
                else:
                    df = pd.read_csv(csv_path)
                data_struct[csv_filename] = df
            except FileNotFoundError:
                print(f"Warning: File {csv_path} not found.")
            except pd.errors.EmptyDataError:
                print(f"Warning: File {csv_path} is empty.")
            except UnicodeDecodeError:
                print(f"Error: {csv_path} contains invalid encoding.")
            except Exception as e:
                print(f"Error loading {csv_path}: {e}")

        # Get image URL
        img_url = submission['image'].get(img_key)
        if img_url:
            images[img_key] = img_url

    file_names = list(data_struct.keys())
    image_values = list(images.values())

    submission = {
        "project": project,
        "file_names": file_names,
        "image_urls": image_values
    }

    return submission

def show_file_and_img(submission,index=0):
    # Show the file and image
    for key in submission.keys():
        if key == 'project':
            print(f"Project: {submission[key]}")
        if key == 'file_names':
            print(f"File Name: {submission[key][index]}")
        elif key == 'image_urls':
            display(Image(url=submission[key][index]))

def get_files(submission):
    keys_list = list(submission['file_names'])

    # Accessing the keys
    first_key = keys_list[0] if len(keys_list) > 0 else None
    second_key = keys_list[1] if len(keys_list) > 1 else None
    third_key = keys_list[2] if len(keys_list) > 2 else None

    files = {
        'first_file': first_key if first_key else None,
        'second_file': second_key if second_key else None,
        'third_file': third_key if third_key else None,
    }

    return files

def main(fig, title=None,subtitle=None,title_xy=dict(x=0.1,y=0.9),date_xy=dict(x=0.05,y=1.18),
         save=True,file_type='svg',clean_columns=False, capwords=None, keep_top_n = False, other=False, topn=None,
         show=True,show_index_and_cols=True,clean_values=False,clean_words=None,dt_index=True,add_the_date=True,groupby=False,groupbyHow='sum',
         date=None,dashed_line=False,annotation_text=None,axis='y1'):
    
    print(f'save:{save}')
    
    if clean_values == True:
        fig.clean_values()

    if groupby:
        fig.group_data(how=groupbyHow)

    if keep_top_n == True:
        if other == False:
            fig.keep_top_n(topn=topn, other=False)
        else:
            fig.keep_top_n(topn=topn, other=True)

    if clean_columns == True:
        fig.clean_columns(capwords=capwords,clean_words=clean_words)
    
    fig.create_fig()

    if show_index_and_cols == True:
        fig.show_index_and_cols()
        
    fig.add_title(title=title,subtitle=subtitle,x=title_xy['x'],y=title_xy['y'])

    if add_the_date == True:
        fig.add_date(date=date,x=date_xy['x'],y=date_xy['y'],dt_index=dt_index)

    if dashed_line:
        fig.add_dashed_line(date=date,annotation_text=annotation_text)

    if show == True:
        fig.show_fig()
    
    if save == True:
        fig.save_fig(filetype=file_type)

def open_json(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print("JSON data loaded successfully!")
        print(data)  # Print the JSON content (optional)
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    return data


