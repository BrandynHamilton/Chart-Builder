import sys

# sys.path.append('E:\Projects\ournetwork\chart_builder\scripts')  
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

import math

# sys.path.append(os.path.join(current_dir, 'pipeline', 'scripts'))

# print("Current working directory:", os.getcwd())
# print("Current directory:", current_dir)

from chart_builder.scripts.utils import dynamic_parameters, top_other_by_col_bubble, top_by_col_bubble, colors, clean_values, clean_values_dollars, ranked_cleaning, to_percentage, rank_by_col, rank_by_columns, normalize_to_percent,calculate_marker_size

import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import plotly.offline as pyo
import plotly.colors as pc
import networkx as nx
# import kaleido

import pandas as pd

combined_colors = colors()

datetime_format = '%b. %d, %Y'

def round_up_to_05(x):
    # Return 0 if x is zero
    if x == 0:
        return 0
    
    # Find the order of magnitude (e.g., millions, billions)
    base = 10 ** (math.floor(math.log10(x)) - 1)
    
    # Scale down to get the leading two digits
    scaled = x / base
    
    # Round to the nearest 0.5 unit or the next major number based on the scaled value
    if scaled <= 10:
        # For numbers between 1 and 10, round to the nearest half (5 or 10)
        if scaled <= 5:
            rounded = 5
        else:
            rounded = 10
    else:
        # For larger numbers, round to the nearest multiple of 5 or 10
        if scaled % 10 <= 5:
            rounded = math.ceil(scaled / 5) * 5
        else:
            rounded = math.ceil(scaled / 10) * 10
    
    # Rescale back to the original magnitude
    return rounded * base

# def generate_ticks(df):
#     # Check if the index is datetime
#     if pd.api.types.is_datetime64_any_dtype(df.index):
#         unique_dates = df.index.drop_duplicates()
#         total_periods = len(df.index)
#         start = 0
#         end = total_periods - 1
#         num_ticks = min(10, total_periods)  # Limit to a maximum of 10 ticks for clarity
        
#         # Generate equally spaced tick indices
#         tick_indices = np.linspace(start, end, num_ticks, dtype=int).tolist()
        
#         # Ensure the last tick is included
#         if end not in tick_indices:
#             tick_indices.append(end)
        
#         # Generate tick values and labels
#         x_ticks = [df.index[i] for i in sorted(set(tick_indices))]
#         x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in x_ticks]

#         return x_ticks, x_tick_labels
#     else:
#         return None, None

def generate_ticks_dynamic(df, plot_width=800, min_tick_spacing=125):
    """
    Generate evenly spaced time-based ticks for datetime index.

    Parameters:
        df (pd.DataFrame): DataFrame with datetime index.
        plot_width (int): Width of the plot in pixels.
        min_tick_spacing (int): Minimum pixel spacing between ticks.

    Returns:
        List of datetime ticks, List of formatted labels.
    """
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        return None, None

    index = df.index.sort_values().unique()
    total_points = len(index)

    # Max number of ticks that can fit in the plot
    max_ticks = max(2, plot_width // min_tick_spacing)

    # Calculate step to downsample index
    step = max(1, total_points // (max_ticks - 1))

    # Select evenly spaced tick indices
    tick_indices = list(range(0, total_points, step))

    # Ensure the last index is included
    if tick_indices[-1] != total_points - 1:
        tick_indices.append(total_points - 1)

    x_ticks = [index[i] for i in tick_indices]
    x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in x_ticks]

    return x_ticks, x_tick_labels

def simple_line_plot(df, title, axes_titles=dict(y1=None, y2=None),color_options=None, mode='lines', area=False, annotations=True, tickprefix=dict(y1=None,y2=None), 
                     ticksuffix=dict(y1=None,y2=None), remove_zero=False, custom_ticks=False,ytickvals=None, yticktext=None,
                      colors=combined_colors, font_size=18, axes_data=dict(y1=None,y2=None), 
                     bgcolor='rgba(0,0,0,0)', legend_orientation='h', tickangle=None, show_legend=False,
                     sort_list=True, dtick=None, max_annotation=False, tickformat=None, tick0=None,
                     traceorder='normal', legend_placement=dict(x=0.01,y=1.1), margin=dict(l=0, r=0, t=0, b=0), legend_font_size=16,text_font_size = 14,
                     line_width=4, marker_size=10,cumulative_sort=False,decimal_places=1,decimals=True,dimensions=dict(width=730,height=400),
                     save=False,fill=None,connectgaps=True,descending=True,text=False,text_freq=1,font_family=None,font_color='black',axes_font_colors=None,
                     file_type='svg',directory='../img',autosize=True,min_tick_spacing=125,
                     custom_annotation=[],ytick_num=6,auto_title=False,buffer=None,datetime_tick=True, legend_background=dict(bgcolor='white',bordercolor='black',
                                                                                                                              borderwidth=1, itemsizing='constant',buffer = 5)):

    "custom_annotation is an array of dates we want annotations for value"

    # print(f'tick0 in func: {tick0}')
    # print(F'sort_list: {sort_list}')

    # print(F'ytickvals: {ytickvals}')
    # print(F'yticktext: {yticktext}')

    space_buffer = " " * legend_background['buffer']

    if bgcolor == 'default':
        bgcolor = 'rgba(0,0,0,0)'
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if not sort_list:
        color_map = {col: colors[idx % len(colors)] for idx, col in enumerate(df.columns)}
        columns_to_plot = list(df.columns)
    else:
        color_order = rank_by_columns(df, cumulative=True, descending=True)
        
        # Determine plotting order based on the latest value
        plot_order = rank_by_columns(df, cumulative=False, descending=descending)

        # print(f"Color order (cumulative): {color_order}")
        # print(f"Plot order (latest value): {plot_order}")

        color_map = {col: colors[idx % len(colors)] for idx, col in enumerate(color_order)}
        columns_to_plot = plot_order

    y1_lineto_show = None
    y2_lineto_show = None

    # print(f'axes_titles at beginning: {axes_titles}')

    if buffer != None:
        if datetime_tick:
            #In the future default to the pd.datatype and just put this after so that datetime_tick is handled more programmatically

            x_buffer = pd.Timedelta(days=buffer)
            x_range_start = df.index.min() - x_buffer
            x_range_end = df.index.max() + x_buffer
        else:
            x_buffer = buffer
            x_range_start = df.index.min() - x_buffer
            x_range_end = df.index.max() + x_buffer
    
    else:
        x_range_start = df.index.min() 
        x_range_end = df.index.max()   

    # print(f'cumulative_sort: {cumulative_sort}')
  
    # Sort columns by descending or ascending
    # sort_list = rank_by_columns(df=df, cumulative=cumulative_sort, descending=descending)
    

    # Print for debugging
    # print(f"descending: {descending}")
    # print(f"columns to plot: {columns_to_plot}")

    
    if axes_font_colors == 'auto' or axes_font_colors is None:
        axes_font_colors = {}

    traces = []

    y1_lineto_show = df[axes_data['y1'][0]].name if auto_title and not axes_titles['y1'] else axes_titles['y1']
    y2_lineto_show = df[axes_data['y2'][0]].name if auto_title and not axes_titles['y2'] else axes_titles['y2']
    
    # print(f'axes_font_colors: {axes_font_colors}')

    # Loop through the y1 columns, applying sorted order
    for idx, y1_col in enumerate(columns_to_plot):
        # print(f'idx: {idx} y1_col: {y1_col}')
        if y1_col not in axes_data['y1']:
            continue  # Skip if y1_col is not in the sorted columns

        # print(f'axes_titles: {axes_titles}')
        
        # print(f'y1_lineto_show: {y1_lineto_show}')
        
        # Assign colors based on position: reverse for ascending
        # print(f'colors: {colors}')
        # if descending:
        #     column_color = colors[idx % len(colors)]  # Normal order for descending
        # else:
        #     column_color = colors[len(columns_to_plot) - idx - 1]  # Reverse order for ascending

        # if 'y1' not in axes_font_colors:
        #     axes_font_colors['y1'] = column_color

        # print(f'axes_font_colors: {axes_font_colors}')

        # print(f'latest val: {df[y1_col].iloc[-1]}')

        if text and text_freq:
            # Create a list to hold text values based on the text frequency
            text_values = [
                f'{tickprefix["y1"] if tickprefix["y1"] else ""}'  # Add tickprefix
                f'{clean_values(df[y1_col][i], decimal_places=decimal_places, decimals=decimals)}'  # Clean the value
                f'{ticksuffix["y1"] if ticksuffix["y1"] else ""}'  # Add ticksuffix
                if i % text_freq == 0 else None for i in range(len(df))
            ]
              # Automatically adjust text position (inside/outside)
        else:
            text_values = ""

        # print(f'y1_col values:{df[y1_col]} ')

        # print(f'color_map: {color_map}')

        color = color_map.get(y1_col, colors[idx % len(colors)])

        # print(f'Processing y1 column: {y1_col} with color: {color}')  # Debugging info

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[y1_col],
            mode=mode,
            text=text_values,
            name=f'{y1_col} ({tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}){space_buffer}',
            stackgroup=None if area == False else 'one',
            line=dict(color=color, width=line_width),
            marker=dict(color=color, size=marker_size), 
            showlegend=show_legend,
            connectgaps=connectgaps,
            fill=fill
        ), secondary_y=False)

    # Check if index is datetime type directly within the function
    if pd.api.types.is_datetime64_any_dtype(df.index):
        datetime_tick = True
    else:
        datetime_tick = False

    # Handling the last value annotation
    if datetime_tick:
        last_text = f'{df.index[-1].strftime(datetime_format)}:<br>{tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
    else:
        last_text = f'{df.index[-1]}:<br>{tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

    # Handling the first value annotation
    if datetime_tick:
        first_text = f'{df.index[0].strftime(datetime_format)}:<br>{tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[0], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
    else:
        first_text = f'{df.index[0]}:<br>{tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[0], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

    # Adding annotations for first and last value
    if annotations:
        # Last value annotation
        fig.add_annotation(dict(
            x=df.index[-1],
            y=df[y1_col].iloc[-1],
            text=last_text,
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=1.5,
            ax=-75,
            ay=-50,
            font=dict(size=text_font_size, family=font_family, color=font_color),
            xref='x',
            yref='y',
            arrowcolor='black'
        ))

        # First value annotation
        fig.add_annotation(dict(
            x=df.index[0],
            y=df[y1_col].iloc[0],
            text=first_text,
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=1.5,
            ax=70,
            ay=-50,
            font=dict(size=text_font_size, family=font_family, color=font_color),
            xref='x',
            yref='y',
            arrowcolor='black'
        ))

    # Handling the maximum value annotation
    if max_annotation:
        max_value = df[y1_col].max()
        max_index = df[df[y1_col] == max_value].index[0]  # Get the index where the maximum value occurs

        if datetime_tick:
            max_text = f'{max_index.strftime(datetime_format)}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(max_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""} (ATH)'
        else:
            max_text = f'{max_index}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(max_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

        fig.add_annotation(dict(
            x=max_index,
            y=max_value,
            text=max_text,
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=1.5,
            ax=-10,
            ay=-50,
            font=dict(size=text_font_size, family=font_family, color=font_color),
            xref='x',
            yref='y',
            arrowcolor='black'
        ))

    # Handling the maximum value annotation
    if custom_annotation:
        for date in custom_annotation:
            if date in df.index:
                y_value = df.loc[date, y1_col]
                annotation_text = f'{date}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(y_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

                fig.add_annotation(dict(
                    x=date,
                    y=y_value,
                    text=annotation_text,
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=1.5,
                    ax=-10,
                    ay=-50,
                    font=dict(size=text_font_size, family=font_family, color=font_color),
                    xref='x',
                    yref='y',
                    arrowcolor='black'  # Customize arrow color if needed
                ))

    # Check for y2 columns, applying sorted order as well
    if axes_data['y2']:
        # print(f'axes_data y2: {axes_data["y2"]}')
        # print(f'columns_to_plot: {columns_to_plot}')
        for idx, y2_col in enumerate(columns_to_plot):
            if y2_col not in axes_data["y2"]:
                # print(f'Skipping y2 column: {y2_col} (not in columns to plot)')
                continue
            if y2_col not in columns_to_plot:
                continue  # Skip if y2_col is not in the sorted columns

            # print(f'idx: {idx} y2_col: {y2_col}')

            # print(f'line to show 2: {y2_lineto_show}')

            # Assign colors based on position: reverse for ascending
            if descending:
                column_color = colors[idx % len(colors)]  # Normal order for descending
            else:
                column_color = colors[len(columns_to_plot) - idx - 1]  # Reverse order for ascending

            if 'y2' not in axes_font_colors:
                axes_font_colors['y2'] = column_color

            color = color_map.get(y2_col, colors[idx % len(colors)])
          
            # print(f'Processing y2 column: {y2_col} with color: {color}') 
            
            # print(f'y2_col values:{df[y2_col]} ') # Debugging info

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[y2_col],
                mode=mode,
                name=f'{y2_col} ({tickprefix["y2"] if tickprefix["y2"] else ""}{clean_values(df[y2_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y2"] if ticksuffix["y2"] else ""}){"          "}',
                stackgroup=None if area == False else 'one',
                line=dict(color=color, width=line_width),
                marker=dict(color=color, size=marker_size), 
                showlegend=show_legend,
                connectgaps=connectgaps,
                fill=fill
            ), secondary_y=True)

    # print(f'axes_font_colors: {axes_font_colors}')

    if custom_ticks:
        y_min = df[axes_data["y1"]].min().min() if df[axes_data["y1"]].min().min() < 0 else 0
        y_max = df[axes_data["y1"]].max().max()

        # print(f'y_min: {y_min}')
        # print(f'y_max: {y_max}')
        
        ticksy = list(np.linspace(y_min, y_max, num=ytick_num, endpoint=True))

        #        Apply round_up_to_05 directly to each tick in ticksy
        ticksy = [round_up_to_05(tick) for tick in ticksy]
        
        if remove_zero:
            ticksy = [tick for tick in ticksy if tick != 0]

        # Format the ticks with prefixes, suffixes, and cleaner values
        formatted_ticks = [
            f"{tickprefix['y1'] if tickprefix['y1'] else ''}{clean_values(tick, decimal_places=0, decimals=False)}{ticksuffix['y1'] if ticksuffix['y1'] else ''}"
            for tick in ticksy
        ]
    else:
        ticksy = None    
    
    # print(f'ticksy: {ticksy}')

    # print(f'[x_range_start, x_range_end]: {[x_range_start, x_range_end]}')

    # if pd.api.types.is_datetime64_any_dtype(df.index):
    #     # import pdb; pdb.set_trace()
    #     # Initialize x_ticks to a default value
    #     x_ticks = None  
    #     unique_dates = df.index.drop_duplicates()
    #     datetime_tick = True
        
    #     if len(unique_dates) >= 3:
    #         inferred_freq = pd.infer_freq(unique_dates)
    #         if inferred_freq in ['M', 'MS']:
    #             total_periods = len(df.index)

    #             # Always include the first and last
    #             start = df.index.min()
    #             end = df.index.max()

    #             # Dynamically adjust num_ticks to ensure even spacing
    #             for num_ticks in range(total_periods, 1, -1):
    #                 step = (total_periods - 1) // (num_ticks - 1)
    #                 if step > 0 and (total_periods - 1) % step == 0:
    #                     break

    #             # Generate ticks
    #             tick_indices = range(0, total_periods, step)
    #             if total_periods - 1 not in tick_indices:
    #                 tick_indices = list(tick_indices) + [total_periods - 1]

    #             x_ticks = [df.index[i] for i in tick_indices]
    #             x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in x_ticks]

    #             print("X-Ticks (Datetime):", x_ticks)
    #             print("X-Tick Labels:", x_tick_labels)
    #     else:
    #         # Handle case with less than 3 dates
    #         x_ticks = unique_dates
    #         x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in unique_dates]
    #         print("X-Ticks (Fewer than 3 Dates):", x_ticks)
    #         print("X-Tick Labels:", x_tick_labels)
    # else:
    #     x_ticks = None  # Ensure x_ticks is defined

    x_ticks, x_tick_labels = generate_ticks_dynamic(df,dimensions['width'],min_tick_spacing)

    # print(f'legend_orientation: {legend_orientation}')

    fig.update_layout(
        legend=dict(
            orientation=legend_orientation,
            yanchor="top",
            y=legend_placement['y'],
            xanchor="left",
            x=legend_placement['x'],
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor=legend_background['bgcolor'],
            bordercolor=legend_background['bordercolor'],
            borderwidth=legend_background['borderwidth'],
            traceorder=traceorder,
            itemsizing=legend_background['itemsizing']
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=15),
        font=dict(size=font_size, family=font_family),
        width=dimensions['width'],
        height=dimensions['height'],
        margin=margin,
        autosize=autosize,
        xaxis_title=dict(
            font=dict(size=font_size, family=font_family, color=font_color)
        ),
        # Ensure yaxis_title is a valid string or fallback to an empty string
        yaxis_title=dict(
            text=y1_lineto_show,   # Show title if not None
            font=dict(size=font_size, family=font_family, color=axes_font_colors.get("y1", font_color))
        ),
        # Handle the yaxis2 title in the same way if needed
        yaxis2_title=dict(
            text=y2_lineto_show,  # Show title if not None
            font=dict(size=font_size, family=font_family, color=axes_font_colors.get("y2", font_color))
        ),
        xaxis=dict(
            tickfont=dict(size=font_size, family=font_family, color=font_color),
            tickangle=tickangle,
            dtick=dtick,
            tickformat=tickformat.get('x', ''),
            range=[x_range_start, x_range_end],
            tickvals=x_ticks if datetime_tick else None,
            # tick_labels = x_tick_labels,
            tick0=tick0
        ),
        yaxis=dict(
            tickfont=dict(size=font_size, family=font_family, color=axes_font_colors.get("y1", font_color)),
            ticksuffix=ticksuffix.get("y1", ""),
            tickprefix=tickprefix.get("y1", ""),
            tickformat=tickformat.get("y1", ""),
            # tickvals=ytickvals,
            # ticktext=yticktext
        ),
        yaxis2=dict(
            tickfont=dict(size=font_size, family=font_family, color=axes_font_colors.get("y2", font_color)),
            overlaying='y',
            ticksuffix=ticksuffix.get("y2", ""),
            tickprefix=tickprefix.get("y2", ""),
            tickformat=tickformat.get("y2", ""),
            # tickvals=ytickvals,
            # ticktext=yticktext
        )
    )

    # Figure
    # pyo.iplot(fig)
    if save == True:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

    # return fig

def simple_bar_plot(df, title, save=False, color_options=None, annotations=True,sort_list=True,
                    colors=combined_colors, font_size=18, remove_zero=False, custom_ticks=False,
                    bgcolor='rgba(0,0,0,0)', legend_orientation='h', tickangle=None, show_legend=False,
                    dtick=None, max_annotation=False, tick0=None, traceorder='normal',
                    legend_placement=dict(x=0.01, y=1.1), margin=dict(l=0, r=0, t=0, b=0), legend_font_size=16, decimals=True,
                    custom_tickval=None, custom_ticktext=None, xtick_prefix=None,connectgaps=True,
                    cumulative_sort=False, decimal_places=1, barmode='stack', text=False,
                    text_freq=1, text_font_size=12, dimensions=dict(width=730, height=400), rangebreaks=None, text_position='outside',
                    axes_data=dict(y1=None, y2=None), tickformat=dict(x=None, y1=None, y2=None), axes_titles=dict(y1=None, y2=None),
                    tickprefix=dict(y1=None, y2=None), ticksuffix=dict(y1=None, y2=None), descending=True,datetime_tick=True,font_family=None,font_color='black',file_type='svg',min_tick_spacing=125,
                    directory='../img',custom_annotation=[],buffer=None,ytick_num=6, auto_title=True,legend_background=dict(bgcolor='white',bordercolor='black',
                                                                                                                              borderwidth=1, itemsizing='constant',buffer = 5)):
    # print(f'testing')
    # print(f'axes_data:{axes_data}')
    if bgcolor == 'default':
        bgcolor = 'rgba(0,0,0,0)'

    space_buffer = " " * legend_background['buffer']
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    y1_lineto_show = None
    y2_lineto_show = None
    # print(f'sort_list: {sort_list}')



    if buffer is not None:
        if datetime_tick and isinstance(df.index, pd.DatetimeIndex):
            x_buffer = pd.to_timedelta(buffer, unit='D')  # safely convert int to timedelta
            x_range_start = df.index.min() - x_buffer
            x_range_end = df.index.max() + x_buffer
        else:
            x_buffer = buffer
            x_range_start = df.index.min() - x_buffer
            x_range_end = df.index.max() + x_buffer
    else:
        x_range_start = df.index.min()
        x_range_end = df.index.max()

    if not sort_list:
        # Keep original column and color order
        color_map = {col: colors[idx % len(colors)] for idx, col in enumerate(df.columns)}
        columns_to_plot = list(df.columns)
    else:
        # Rank columns for consistent color assignment
        color_order = rank_by_columns(df, cumulative=cumulative_sort, descending=True)  # Rank largest to smallest for consistent colors
        plot_order = rank_by_columns(df, cumulative=cumulative_sort, descending=descending)  # Plot in user-defined order

        # print(f"Color order (largest first for color): {color_order}")
        # print(f"Plot order (user-defined): {plot_order}")

        # Assign colors based on the ranked order (largest series gets the first color)
        color_map = {col: colors[color_order.get_loc(col) % len(colors)] for col in plot_order}

        # Plot order determines the sequence of plotting
        columns_to_plot = list(plot_order)

    # Print for debugging
    # print(f"descending: {descending}")
    # print(f"columns to plot: {columns_to_plot}")
    # print(f'tick0: {tick0}')

    # tick0 = df.index.min()

    # print(f'new tick0: {tick0}')

    # if not descending:
    #     # Reverse the colors for the plotting order
    #     reversed_colors = [color_map[col] for col in reversed(columns_to_plot)]
    #     color_map = {col: reversed_colors[idx] for idx, col in enumerate(columns_to_plot)}
    # print(f'reversed color map: {color_map}')
    # print(f'axes_titles: {axes_titles}')
    
    # Assign colors based on position (last-ranked gets the first color in reversed list)
    for idx, y1_col in enumerate(columns_to_plot):
        # print(f'idx: {idx}, y: {y1_col}')
        if y1_col not in axes_data["y1"]:
            continue  # Skip if the column isn't in the sorted list

        if auto_title == True:
            y1_lineto_show = y1_col if axes_titles["y1"] == None else axes_titles["y1"]
        elif auto_title == False:
            y1_lineto_show = axes_titles["y1"]

        # print(F'auto_title: {auto_title}')
        # print(F'y1_lineto_show: {y1_lineto_show}')
        # Assign colors based on position: reverse for ascending
            
        if text and text_freq:
            # Create a list to hold text values based on the text frequency
            text_values = [
                f'{tickprefix["y1"] if tickprefix["y1"] else ""}'  # Add tickprefix
                f'{clean_values(df[y1_col].iloc[i], decimal_places=decimal_places, decimals=decimals)}'  # Use .iloc for positional indexing
                f'{ticksuffix["y1"] if ticksuffix["y1"] else ""}'  # Add ticksuffix
                if i % text_freq == 0 else None for i in range(len(df))
            ]
              # Automatically adjust text position (inside/outside)
        else:
            text_values = ""

        # print(f'index: {df.index}')
        # print(f'vals: {df[y1_col]}')

        color = color_map[y1_col]

        # print(f'processing {y1_col} with color {color}')
      
        # Add the trace for each y1 column with the color assignment
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[y1_col],
            name=f'{y1_col} ({tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}){space_buffer}',
            marker=dict(color=color),
            text=text_values,  # Use the filtered text values based on frequency
            textposition=text_position,  # Position of the text on the bars
            showlegend=show_legend,
            textfont=dict(
                family=font_family,  # Use IBM Plex Mono font
                size=text_font_size,  # Set font size
                color="black"  # Set text color to black
            )
        ), secondary_y=False)

        # print(f'datetime_tick: {datetime_tick}')

        # if pd.api.types.is_datetime64_any_dtype(df.index):
        #     datetime_tick = True
        # else:
        #     datetime_tick = False

        # Handling the last value annotation
        if datetime_tick:
            last_text = f'{df.index[-1].strftime(datetime_format)}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
        else:
            last_text = f'{df.index[-1]}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

        # Handling the first value annotation
        if datetime_tick:
            first_text = f'{df.index[0].strftime(datetime_format)}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[0], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
        else:
            first_text = f'{df.index[0]}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[0], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

        # Adding annotations for first and last value
        if annotations:
            # Last value annotation
            fig.add_annotation(dict(
                x=df.index[-1],
                y=df[y1_col].iloc[-1],
                text=last_text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=1.5,
                ax=-100,
                ay=-50,
                font=dict(size=text_font_size, family=font_family, color=font_color),
                xref='x',
                yref='y',
                arrowcolor='black'
            ))

            # First value annotation
            fig.add_annotation(dict(
                x=df.index[0],
                y=df[y1_col].iloc[0],
                text=first_text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=1.5,
                ax=100,
                ay=-50,
                font=dict(size=text_font_size, family=font_family, color=font_color),
                xref='x',
                yref='y',
                arrowcolor='black'
            ))

        # Handling the maximum value annotation
        if max_annotation:
            max_value = df[y1_col].max()
            max_index = df[df[y1_col] == max_value].index[0]  # Get the index where the maximum value occurs

            if datetime_tick:
                max_text = f'{max_index.strftime(datetime_format)}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(max_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""} (ATH)'
            else:
                max_text = f'{max_index}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(max_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

            fig.add_annotation(dict(
                x=max_index,
                y=max_value,
                text=max_text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=1.5,
                ax=-10,
                ay=-50,
                font=dict(size=text_font_size, family=font_family, color=font_color),
                xref='x',
                yref='y',
                arrowcolor='black'
            ))

        if custom_annotation:
            for date in custom_annotation:
                if date in df.index:
                    y_value = df.loc[date, y1_col]
                    annotation_text = f'{date}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(y_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

                    fig.add_annotation(dict(
                        x=date,
                        y=y_value,
                        text=annotation_text,
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowwidth=1.5,
                        ax=-10,
                        ay=-50,
                        font=dict(size=text_font_size, family=font_family, color=font_color),
                        xref='x',
                        yref='y',
                        arrowcolor='black'  # Customize arrow color if needed
                    ))

    # Traces for y2 columns (similar logic)
    if axes_data['y2']:
        for idx, y2_col in enumerate(columns_to_plot):
            if y2_col not in axes_data["y2"]:
                # print(f'Skipping y2 column: {y2_col} (not in columns to plot)')
                continue

            if auto_title == True:
                y2_lineto_show = y2_col if axes_titles["y2"] == None else axes_titles["y2"]
            elif auto_title == False:
                y2_lineto_show = axes_titles["y2"]
            
            # Determine color based on sorted order for y2
            sorted_index = columns_to_plot.index(y2_col)
            line_color = colors[(sorted_index + len(axes_data["y1"])) % len(colors)]
            # print(f'Processing y2 column: {y2_col} with color: {line_color}')
            
            fig.add_trace(go.Bar(
                x=df.index,
                y=df[y2_col],
                name=f'{y2_col}',
                marker=dict(color=line_color),
                textposition=text_position,
                showlegend=show_legend,
            ), secondary_y=True)

    if custom_ticks:
        y_min = df[axes_data["y1"]].min().min() if df[axes_data["y1"]].min().min() < 0 else 0
        y_max = df[axes_data["y1"]].max().max()
        
        # Generate tick values using np.linspace with rounded bounds
        ticksy = list(np.linspace(y_min, y_max, num=ytick_num, endpoint=True))
        ticksy = [round_up_to_05(tick) for tick in ticksy]
        # print(f'ticksy: {ticksy}')
        if remove_zero:
            ticksy = [tick for tick in ticksy if tick != 0]
        
        formatted_ticks = [
            f"{tickprefix['y1'] if tickprefix['y1'] else ''}{clean_values(tick, decimal_places=0, decimals=False)}{ticksuffix['y1'] if ticksuffix['y1'] else ''}"
            for tick in ticksy
        ]
        # print(f'formatted_ticks: {formatted_ticks}')
    else:
        ticksy = None

    # if pd.api.types.is_datetime64_any_dtype(df.index):
    #     # Initialize x_ticks to a default value
    #     x_ticks = None  
    #     unique_dates = df.index.drop_duplicates()
    #     datetime_tick = True
        
    #     if len(unique_dates) >= 3:
    #         inferred_freq = pd.infer_freq(unique_dates)
    #         if inferred_freq in ['M', 'MS']:
    #             total_periods = len(df.index)

    #             # Always include the first and last
    #             start = df.index.min()
    #             end = df.index.max()

    #             # Dynamically adjust num_ticks to ensure even spacing
    #             for num_ticks in range(total_periods, 1, -1):
    #                 step = (total_periods - 1) // (num_ticks - 1)
    #                 if step > 0 and (total_periods - 1) % step == 0:
    #                     break

    #             # Generate ticks
    #             tick_indices = range(0, total_periods, step)
    #             if total_periods - 1 not in tick_indices:
    #                 tick_indices = list(tick_indices) + [total_periods - 1]

    #             x_ticks = [df.index[i] for i in tick_indices]
    #             x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in x_ticks]

    #             print("X-Ticks (Datetime):", x_ticks)
    #             print("X-Tick Labels:", x_tick_labels)
    #     else:
    #         # Handle case with less than 3 dates
    #         x_ticks = unique_dates
    #         x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in unique_dates]
    #         print("X-Ticks (Fewer than 3 Dates):", x_ticks)
    #         print("X-Tick Labels:", x_tick_labels)
    # else:
    #     x_ticks = None  # Ensure x_ticks is defined

    x_ticks, x_tick_labels = generate_ticks_dynamic(df,dimensions['width'],min_tick_spacing)

    # print(f'x_ticks: {x_ticks}')

    fig.update_layout(
        barmode=barmode,
        legend=dict(
            orientation=legend_orientation,
            yanchor=legend_background['yanchor'],
            y=legend_placement['y'],  # Position above the plot area
            xanchor=legend_background['xanchor'],
            x=legend_placement['x'],  # Position to the left of the plot area
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor=legend_background['bgcolor'],
            bordercolor=legend_background['bordercolor'],
            borderwidth=legend_background['borderwidth'],
            traceorder=traceorder,
            itemsizing=legend_background['itemsizing']
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=text_font_size),
        font=dict(size=font_size, family=font_family),
        width=dimensions['width'],
        height=dimensions['height'],
        margin=margin,
        autosize=True,
        xaxis_title=dict(
            font=dict(size=font_size, family=font_family, color=font_color)
        ),
        # Ensure yaxis_title is a valid string or fallback to an empty string
        yaxis_title=dict(
            text=y1_lineto_show if y1_lineto_show else None,  # Show title if not None
            font=dict(size=font_size, family=font_family, color=font_color)
        ),
        # Handle the yaxis2 title in the same way if needed
        yaxis2_title=dict(
             text=y2_lineto_show if y2_lineto_show else None,  # Show title if not None
            font=dict(size=font_size, family=font_family, color=font_color)
        ),
        xaxis=dict(
            tickfont=dict(size=font_size, family=font_family, color=font_color),
            tickangle=tickangle,
            dtick=dtick,
            tickformat=tickformat.get('x', ''),
            tick0=tick0,
            range=[x_range_start, x_range_end],
            tickvals=x_ticks if datetime_tick else None,
            ticktext=custom_ticktext,
            tickprefix=xtick_prefix,
            rangebreaks=rangebreaks
        ),
        yaxis=dict(
            tickvals=ticksy,
            ticktext=formatted_ticks if custom_ticks else None,
            tickfont=dict(size=font_size, family=font_family, color=font_color),
            ticksuffix=ticksuffix.get("y1", ""),
            tickprefix=tickprefix.get("y1", ""),
            tickformat=tickformat.get("y1", ""),
        ),
        yaxis2=dict(
            tickfont=dict(size=font_size, family=font_family, color=font_color),
            overlaying='y',
            ticksuffix=ticksuffix.get("y2", ""),
            tickprefix=tickprefix.get("y2", ""),
            tickformat=tickformat.get("y2", "")
        )
    )

    if save == True:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

def line_and_bar(df, title, save=False, bar_col=None, line_col=None, mode='lines', area=False, tickprefix=dict(y1=None, y2=None), ticksuffix=dict(y1=None, y2=None),
                 colors=combined_colors, font_size=18, y2_axis=True, tickangle=None, remove_zero=False, custom_ticks=False,
                 bgcolor='rgba(0,0,0,0)', legend_orientation='v', dtick=None, tick0=None,line_width=4, marker_size=10,cumulative_sort=True,
                 traceorder='normal', line_color='#2E2E2E', legend_placement=dict(x=0.01, y=1.1),text_font_size=14,text=False, text_freq=1, text_position='outside',
                 bar_color=None, fill=None, margin=dict(l=0, r=0, t=0, b=0), legend_font_size=16, decimals=True, decimal_places=1,
                 xtitle=None, barmode='stack', axes_title=dict(y1=None, y2=None), dimensions=dict(width=730, height=400), auto_title=True,min_tick_spacing=125,
                 tickformat=dict(x=None, y1=".2s", y2=".2s"),font_family=None,font_color='black',file_type='svg',directory='../img',custom_annotation=[],buffer=None,
                 ytick_num=6,axes_font_colors=dict(y1='black',y2='black'),show_legend=True, legend_background=dict(bgcolor='white',bordercolor='black',
                                                                                                                              borderwidth=1, itemsizing='constant',buffer = 5),
                                                                                                                              autosize=True):
    # print(f'line_width: {line_width}')
    if bgcolor == 'default':
        bgcolor = 'rgba(0,0,0,0)'
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    space_buffer = " " * legend_background['buffer']

    # Define a small buffer for x-axis range extension (e.g., 1 day on each side)
    if buffer != None:

        if isinstance(df.index, pd.DatetimeIndex):
            # If the index is a datetime index, use timedelta
            x_buffer = pd.Timedelta(days=buffer)
            x_range_start = df.index.min() - x_buffer
            x_range_end = df.index.max() + x_buffer
        else:
            # If the index is not datetime, use a numeric buffer
            x_buffer = buffer
            x_range_start = df.index.min() - x_buffer
            x_range_end = df.index.max() + x_buffer
    
    else:
        x_range_start = df.index.min() 
        x_range_end = df.index.max() 

    # print(f'axes_font_colors param: {axes_font_colors}')

    if axes_font_colors == 'auto':
        axes_font_colors = {'y1': colors[0], 'y2': line_color}

    # Set y-axis titles based on auto_title and axes_title
    if auto_title:
        axes_title['y1'] = bar_col[0] if bar_col and not axes_title['y1'] else axes_title['y1']
        axes_title['y2'] = line_col[0] if line_col and not axes_title['y2'] else axes_title['y2']

    if y2_axis == False:
        tickprefix["y2"] = tickprefix["y1"]

    filtered_colors = [color for color in colors if color not in [line_col, 'black']]
    filtered_iter = iter(filtered_colors)

    # print(f'axes titles: {axes_title}')
    
    color_iter = iter(colors)  # Create an iterator for the colors
    rev_color_iter = reversed(colors[:-1])
    # print(f'reversed color iter: {rev_color_iter}')
    # print(f'line_width at line col: {line_width}')

    for i, col in enumerate(line_col):
        color = line_color if i == 0 else next(rev_color_iter, "black")
        # print(f'color for line{color}')
        # print(f'line col: {df[col]}')
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            name=f'{col} ({tickprefix["y2"] if tickprefix["y2"] else ""}{clean_values(df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places)}{ticksuffix["y2"] if ticksuffix["y2"] else ""}){space_buffer}',
            mode=mode,
            stackgroup=None if area == False else 'one',
            line=dict(color=color, width=line_width),
            marker=dict(color=color, size=marker_size),
            showlegend=show_legend
        ), secondary_y=y2_axis)

    if fill == None:
        # Add bar traces without specifying `width` to maintain default spacing
        for col in bar_col:
            if text and text_freq:
                # Create a list to hold text values based on the text frequency
                text_values = [
                    f'{tickprefix["y1"] if tickprefix["y1"] else ""}'  # Add tickprefix
                    f'{clean_values(df[col].iloc[i], decimal_places=decimal_places, decimals=decimals)}'  # Use .iloc for positional indexing
                    f'{ticksuffix["y1"] if ticksuffix["y1"] else ""}'  # Add ticksuffix
                    if i % text_freq == 0 else None for i in range(len(df))
                ]
                    # Automatically adjust text position (inside/outside)
            else:
                text_values = ""

            color = next(filtered_iter, colors[1])  # Get the next color, fallback to first color if exhausted
            # print(f'color for bar{color}')
            fig.add_trace(go.Bar(
                x=df.index,
                y=df[col],
                text=text_values,  # Use the filtered text values based on frequency
                name=f'{col} ({tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}){space_buffer}',
                marker=dict(color=color if bar_color == None else bar_color),
                showlegend=show_legend
            ), secondary_y=False)
    else:
        for col in bar_col:
            color = next(color_iter, colors[1])  # Get the next color, fallback to first color if exhausted
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                name=f'{col} ({tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}){space_buffer}',
                marker=dict(color=color if bar_color == None else bar_color),
                fill=fill,  # This creates the area chart by filling to the x-axis (y=0)
                showlegend=show_legend
            ), secondary_y=False)

    if custom_annotation:
        for date in custom_annotation:
            if date in df.index:
                y_value = df.loc[date, bar_col[0]]
                annotation_text = f'{pd.to_datetime(date).strftime(datetime_format)}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(y_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

                fig.add_annotation(dict(
                    x=date,
                    y=y_value,
                    text=annotation_text,
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=1.5,
                    ax=25,
                    ay=-50,
                    font=dict(size=text_font_size, family=font_family, color=font_color),
                    xref='x',
                    yref='y',
                    arrowcolor='black'  # Customize arrow color if needed
                ))

    if custom_ticks:
        figy = df[bar_col[0]]
        y_min = figy.min() if figy.min() < 0 else 0
        y_max = figy.max()
        ticksy = list(np.linspace(y_min, y_max, num=ytick_num, endpoint=True))

        #        Apply round_up_to_05 directly to each tick in ticksy
        ticksy = [round_up_to_05(tick) for tick in ticksy]
        if remove_zero:
            ticksy = [tick for tick in ticksy if tick != 0]
        formatted_ticks = [
        f"{tickprefix['y1'] if tickprefix['y1'] else ''}{clean_values(tick, decimal_places=0, decimals=False)}{ticksuffix['y1'] if ticksuffix['y1'] else ''}"
        for tick in ticksy]
    else:
        ticksy = None  # Default to None if not using custom ticks

    # Convert datetime index to timestamps for linspace calculation
    # if pd.api.types.is_datetime64_any_dtype(df.index):
    #     # Initialize x_ticks to a default value
    #     x_ticks = None  
    #     unique_dates = df.index.drop_duplicates()
    #     datetime_tick = True
        
    #     if len(unique_dates) >= 3:
    #         inferred_freq = pd.infer_freq(unique_dates)
    #         if inferred_freq in ['M', 'MS']:
    #             total_periods = len(df.index)

    #             # Always include the first and last
    #             start = df.index.min()
    #             end = df.index.max()

    #             # Dynamically adjust num_ticks to ensure even spacing
    #             for num_ticks in range(total_periods, 1, -1):
    #                 step = (total_periods - 1) // (num_ticks - 1)
    #                 if step > 0 and (total_periods - 1) % step == 0:
    #                     break

    #             # Generate ticks
    #             tick_indices = range(0, total_periods, step)
    #             if total_periods - 1 not in tick_indices:
    #                 tick_indices = list(tick_indices) + [total_periods - 1]

    #             x_ticks = [df.index[i] for i in tick_indices]
    #             x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in x_ticks]

    #             print("X-Ticks (Datetime):", x_ticks)
    #             print("X-Tick Labels:", x_tick_labels)
    #     else:
    #         # Handle case with less than 3 dates
    #         x_ticks = unique_dates
    #         x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in unique_dates]
    #         print("X-Ticks (Fewer than 3 Dates):", x_ticks)
    #         print("X-Tick Labels:", x_tick_labels)
    # else:
    #     x_ticks = None  # Ensure x_ticks is defined

    x_ticks, x_tick_labels = generate_ticks_dynamic(df,dimensions['width'],min_tick_spacing)

    fig.update_layout(
        barmode=barmode,
        autosize=autosize,
        legend=dict(
            orientation=legend_orientation,
            yanchor="top",
            y=legend_placement['y'],
            xanchor="left",
            x=legend_placement['x'],
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor=legend_background['bgcolor'],
            bordercolor=legend_background['bordercolor'],
            borderwidth=legend_background['borderwidth'],
            traceorder=traceorder,
            itemsizing=legend_background['itemsizing']
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        font=dict(size=font_size, family=font_family, color=font_color),
        width=dimensions['width'],
        height=dimensions['height'],
        margin=margin
    )

    fig.update_xaxes(
        title_text=xtitle,
        title_font=dict(size=font_size, family=font_family, color=font_color),
        tickfont=dict(size=font_size, family=font_family, color=font_color),
        tickangle=tickangle,
        range=[x_range_start, x_range_end],  # Extend range to avoid clipping
        tickvals=x_ticks,
        dtick=dtick,
        tickformat=tickformat['x'],
        tick0=tick0
    )

    # print(f'axes_title["y1"]: {axes_title["y1"]}')
    # print(f'axes_font_colors["y1"]: {axes_font_colors["y1"]}')
    
    fig.update_yaxes(
        title_text=axes_title["y1"],
        tickvals=ticksy if custom_ticks else None,
        ticktext=formatted_ticks if custom_ticks else None,
        title_font=dict(size=font_size, family=font_family, color=axes_font_colors['y1']),
        tickfont=dict(size=font_size, family=font_family, color=axes_font_colors['y1']),
        ticksuffix=ticksuffix["y1"],
        tickprefix=tickprefix["y1"],
        tickformat=tickformat["y1"]
    )

    fig.update_yaxes(
        secondary_y=True,
        title_text=axes_title["y2"],
        title_font=dict(size=font_size, family=font_family, color=axes_font_colors['y2']),
        tickfont=dict(size=font_size, family=font_family, color=axes_font_colors['y2']),
        ticksuffix=ticksuffix["y2"],
        tickprefix=tickprefix["y2"],
        tickformat=tickformat["y2"]
    )

    if save:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

def sorted_multi_line(df, title, save=False, colors=combined_colors, mode='lines', col=None, sort_col=None,user_sort_list=None, user_color_map=None,
                      sort_list=True, area=False, tickprefix=None, ticksuffix=None, font_size=18,y_log=False,
                      bgcolor='rgba(0,0,0,0)', legend_orientation='h', tickangle=None,axes_titles=dict(y1=None, y2=None),
                      traceorder='normal', legend_placement=dict(x=0.01, y=1.1), margin=dict(l=0, r=0, t=0, b=0),
                      legend_font_size=14, tickformat=dict(x="%b %y", y1=".2s", y2=".2s"), dtick=None, decimals=True, decimal_places=1,
                      dimensions=dict(width=730, height=400), remove_zero=False, custom_ticks=False,min_tick_spacing=125,
                      connectgaps=True, descending=True, show_legend=True, tick0=None,font_family=None,font_color='black',file_type='svg'
                      ,directory='../img',custom_annotation=[],cumulative_sort=False,line_width=4,marker_size=10,marker_col = None,
                      annotations=False,max_annotation=False,text_font_size=14,legend_background=dict(bgcolor='white',bordercolor='black',
                                                                                                                              borderwidth=1, itemsizing='constant',buffer = 5),
                                                                                                                              autosize=True):
    
    if marker_col is not None:
        min_marker = df[marker_col].min()
        max_marker = df[marker_col].max()
        df['marker_size'] = ((df[marker_col] - min_marker) / (max_marker - min_marker) * 10) + 5  # Normalize to 5-15 range
    else:
        df['marker_size'] = marker_size  # Default size if no marker column is provided

    combined_colors = colors

    space_buffer = " " * legend_background['buffer']

    # print(f'tick0: {tick0}')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    traces = []

    x_buffer = pd.Timedelta(days=15)
    x_range_start = df.index.min() 
    x_range_end = df.index.max() 

    if not user_sort_list and not user_color_map:

        sort_list, color_map = rank_by_col(
            df=df, sort_col=sort_col, num_col=col, descending=descending,
            cumulative_sort=cumulative_sort, colors=colors
        )
    else:
        sort_list = user_sort_list
        color_map = user_color_map

    # print(f'sort_list: {sort_list}')
    # print(f'color_map: {color_map}')

    # Plot using latest value sort and cumulative color mapping
    for idx, i in enumerate(sort_list):
        i_df = df[df[sort_col] == i]
        x=i_df.index,
        y=i_df[col],
        # print(f'i: {i}')
        # print(f'col: {col}')
        # print(f'idx: {idx}')
        # print(f'i_df {i_df}')
        # print(f'x, y: {x, y}')
        # Use the cumulative color map if available; otherwise, fallback to index-based colors
        color = color_map.get(i, colors[idx % len(colors)])

        traces.append(go.Scatter(
            x=i_df.index,
            y=i_df[col],
            name=f'{i} ({tickprefix if tickprefix else ""}{clean_values(i_df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places) if i_df.index.max() == df.index.max() else 0}{ticksuffix if ticksuffix else ""}){space_buffer}',
            line=dict(color=color, width=line_width),
            marker=dict(
                color=color,
                size=i_df['marker_size'].tolist()  # Assign dynamic sizes based on marker_col
            ),
            mode=mode,
            connectgaps=connectgaps,
            stackgroup=None if not area else 'one',
            showlegend=show_legend
        ))

        # print(f'idx: {idx}')
        # print(f'custom_annotation: {custom_annotation}')

        if idx == 0:
            if custom_annotation:
                for date in custom_annotation:
                    # print(f'i_df index: {i_df}')
                    # print(f'custom_annotation: {date}')
                    if date in i_df.index:
                        y_value = i_df.loc[date, col]
                        # print(f'y_value: {y_value}')
                        annotation_text = f'{date}: {tickprefix if tickprefix else ""}{clean_values(y_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix if ticksuffix else ""}'

                        fig.add_annotation(dict(
                            x=date,
                            y=y_value,
                            text=annotation_text,
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1.5,
                            arrowwidth=1.5,
                            ax=-10,
                            ay=-50,
                            font=dict(size=text_font_size, family=font_family, color=font_color),
                            xref='x',
                            yref='y',
                            arrowcolor='black'  # Customize arrow color if needed
                        ))

    for trace in traces:
        fig.add_trace(trace, secondary_y=False)

    x_ticks, x_tick_labels = generate_ticks_dynamic(df,dimensions['width'],min_tick_spacing)

    if custom_ticks:
        figy = df[col] 
        y_min = figy.min() if figy.min() < 0 else 0
        y_max = figy.max() * 1.25
        ticksy = list(np.linspace(y_min, y_max, num=5, endpoint=True))

        #        Apply round_up_to_05 directly to each tick in ticksy
        ticksy = [round_up_to_05(tick) for tick in ticksy]

        if remove_zero:
            ticksy = [tick for tick in ticksy if tick != 0]
        
        formatted_ticks = [
        f"{tickprefix if tickprefix else ''}{clean_values(tick, decimal_places=0, decimals=False)}{ticksuffix if ticksuffix else ''}"
        for tick in ticksy
    ]
        
    else:
        ticksy = None  # Default to None if not using custom ticks

    # print(f'formatted_tick: {formatted_ticks}')
    # print(f'decimals: {decimals}')
    # print(f'decimal places: {decimal_places}')
    

    fig.update_layout(
        autosize=True,
        legend=dict(
            orientation=legend_orientation,
            yanchor=legend_background['yanchor'],
            y=legend_placement['y'],  # Position above the plot area
            xanchor=legend_background['xanchor'],
            x=legend_placement['x'],  # Position to the left of the plot area
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor=legend_background['bgcolor'],
            bordercolor=legend_background['bordercolor'],
            borderwidth=legend_background['borderwidth'],
            traceorder=traceorder,
            itemsizing=legend_background['itemsizing']
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=15),
        font=dict(size=font_size, family=font_family, color=font_color),
        width=dimensions['width'],
        height=dimensions['height'],
        margin=margin
    )

    # print(f'x_ticks: {x_ticks}')
    if y_log:
        fig.update_yaxes(type='log', secondary_y=False)
    
    fig.update_layout(
        xaxis=dict(
            range=[x_range_start, x_range_end],
            tickvals=x_ticks,  # Explicitly set tick values to include min and max of the index
            tickangle=tickangle,
            tickfont=dict(size=font_size, family=font_family, color=font_color),
            tickformat=tickformat['x'],
            dtick=dtick,
            tick0=tick0
        ),

        yaxis=dict(
            tickvals=ticksy if custom_ticks else None,
            ticksuffix=ticksuffix,
            ticktext=formatted_ticks if custom_ticks else None,
            tickprefix=tickprefix,
            tickfont=dict(size=font_size, family=font_family, color=font_color),
            tickformat=tickformat['y1'],
            title=dict(
            text=axes_titles['y1'],  # Passing the title text
            font=dict(size=font_size, family=font_family, color=font_color)  # Customizing the title font
            )

        )
    )

    if save:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

def ranked_bar_chart(df, title, save=False, colors=combined_colors, barmode='stack', col=None, sort_col=None,
                     tickprefix=None, ticksuffix=None, font_size=18,
                     bgcolor='rgba(0,0,0,0)', legend_orientation='h', tickangle=None, textposition="outside", orientation="h",
                     legend_placement=dict(x=0.01, y=1.1), minsize=16, legend_font_size=16, margin=dict(l=0, r=0, t=0, b=0),
                     showlegend=False, decimals=True, traceorder='normal', decimal_places=1, to_reverse=False,
                     tickformat=',.0f', itemsizing='constant', trace_text=14, dimensions=dict(width=730, height=400), descending=True,
                     use_sort_list=True,show_text=True,font_family=None,font_color='black',file_type='svg',directory='../img',
                     use_single_color=False,discrete=False):

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    combined_colors = colors

    primary_color = colors[0] if use_single_color else None

    # print(f'combined_colors: {combined_colors}')
    # print(f'primary_color: {primary_color}')

    traces = []
    # print(f'df sort order before ranked cleaning: {df[sort_col].unique()}')

    df, sort_list = ranked_cleaning(df, col, sort_col, descending=descending,use_sort_list=use_sort_list)
    # print(f'df: {df}')

    # print(f'Decimal Places: {decimal_places}')

    # if use_sort_list:
    #     sort_list = sort_list
    # else:
    #     sort_list = df.columns

    # print(f'sort_list: {sort_list}')

    if to_reverse:
        sort_list = reversed(sort_list)

    # print(f'sort list: {sort_list}')
    for idx, i in enumerate(sort_list):
        if showlegend:
            # print(f'i: {i} \nidx: {idx} \nprefix: {ticksuffix}')
            name = f'{i} ({tickprefix if tickprefix else ""}{clean_values(df[df[sort_col] == i][col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix if ticksuffix else ""}){"                  "}' 
            text = None
            y = idx
        else:
            if show_text:
                # print(f'i: {i} \nidx: {idx} \nprefix: {ticksuffix}')
                name = None
                # Add buffer (spaces) at the end of each formatted text value
                text = df[df[sort_col] == i][col].apply(
                    lambda x: f'{tickprefix if tickprefix else ""}{clean_values(x, decimals=decimals, decimal_places=decimal_places)}{ticksuffix if ticksuffix else ""}'
                )
                y = i
            else:
                # print(f'i: {i} \nidx: {idx} \nprefix: {ticksuffix}')
                name = None
                text = None
                y = i


        # print(f'idx: {idx} i: {i}')

        # Determine the color based on descending order
        if use_single_color:
            color = primary_color  # Use the first color in the list
        elif descending:
            color = combined_colors[idx % len(combined_colors)]  # Normal order for descending
        else:
            color = combined_colors[len(sort_list) - idx - 1]  # Reverse order for ascending

        # print(f'use_single_color:{use_single_color}')
        # print(f'color: {color}')

        if orientation == 'v':  # Vertical orientation
            x = [i]  # Categorical value on the x-axis
            y = df[df[sort_col] == i][col]  # Numeric value on the y-axis
        else:  # Horizontal orientation
            x = df[df[sort_col] == i][col]
            y = [i]  # Categorical value on the y-axis

        traces.append(go.Bar(
            y=y,
            x=x,
            orientation=orientation,
            text=text,
            textfont=dict(size=trace_text, color=font_color),  # Change this to adjust font size
            textposition=textposition,
            name=name,
            marker=dict(color=color),
            showlegend=showlegend
        ))

    for trace in traces:
        fig.add_trace(trace, secondary_y=False)

    fig.update_layout(
        barmode=barmode,
        autosize=True,
        legend=dict(
            orientation=legend_orientation,
            yanchor="top",
            y=legend_placement['y'],  # Position above the plot area
            xanchor="left",
            x=legend_placement['x'],  # Position to the left of the plot area
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor='rgba(0,0,0,0)',  # Make the legend background transparent
            traceorder=traceorder,
            itemsizing=itemsizing
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=minsize),  # Adjust minsize as needed
        font=dict(size=font_size, family=font_family, color=font_color),  # General font size, can be adjusted as needed
    )

    # Adjust layout size
    fig.update_layout(
        width=dimensions['width'],
        height=dimensions['height'],  # Adjust as needed
        margin=margin
    )

    index_length = len(df.index)

    # print(f'text: {show_text}')

    if orientation == 'v':
        xtickangle = tickangle
        ytickangle = 0
        if not showlegend:
            ytickprefix = tickprefix
            yticksuffix = ticksuffix
            xtickprefix = None  # No prefix for x-axis if legend is not shown
            xticksuffix = None  # No suffix for x-axis if legend is not shown

            if show_text:
                ticktext = list(range(index_length)) 
                tickvals = [""] * index_length
            else:
                ticktext = None
                tickvals = None
            
        else:
            ytickprefix = tickprefix
            yticksuffix = ticksuffix
            tickvals = list(range(index_length))  # Tick values based on index length for y-axis
            ticktext = [""] * index_length  # No specific ticktext if showing legend
            xtickprefix = None  # Adjust if needed based on your requirements
            xticksuffix = None  # Adjust if needed based on your requirements
        
        xtickvals = None
        xticktext = None

    else:  # Horizontal orientation
        xtickangle = 0
        ytickangle = tickangle
        if not showlegend:
            # print(f'no legend, horizontal')
            ytickprefix = None
            yticksuffix = None
            tickvals = None  # No specific tick values for y-axis
            ticktext = [""] * index_length  # Empty strings for tick labels on the y-axis
            xtickprefix = tickprefix  # Use tickprefix for x-axis if not showing legend
            xticksuffix = ticksuffix  # Use ticksuffix for x-axis if not showing legend

            if show_text:
                xtickvals = list(range(index_length)) 
                xticktext = [""] * index_length
            else:
                xtickvals = None
                xticktext = None

        else:
            # print(f'legend, horizontal')
            ytickprefix = None
            yticksuffix = None
            tickvals = list(range(index_length))  # No specific tick values for y-axis
            ticktext = [""] * index_length  # No specific ticktext if showing legend
            xtickprefix = tickprefix  # Use tickprefix for x-axis if showing legend
            xticksuffix = ticksuffix  # Use ticksuffix for x-axis if showing legend

    # print(f'ytickvals: {tickvals}')
    # print(f'yticktext: {ticktext}')
    # print(f'ytickprefix: {ytickprefix}')
    # print(f'xtickprefix: {xtickprefix}')
    # print(f'xtickvals: {xtickvals if xtickvals else ""}')
    # print(f'xticktext: {xticktext if xtickvals else ""}')

    fig.update_layout(
        xaxis_title=dict(
            font=dict(size=font_size, family=font_family, color=font_color),
        ),
        xaxis=dict(tickangle=xtickangle,
                   tickfont=dict(size=font_size, family=font_family, color=font_color),
                   tickprefix=xtickprefix,
                   ticksuffix=xticksuffix,
                   tickformat=tickformat,
                   tickvals=xtickvals,
                   ticktext=xticktext
                   ),

        yaxis=dict(tickprefix=ytickprefix,
                   ticksuffix=yticksuffix,
                   tickangle=ytickangle,
                   tickfont=dict(size=font_size, family=font_family, color=font_color),
                   tickvals=tickvals,  # Set tick values to blank if not showing legend
                   ticktext=ticktext),
        
        
                   

    )

    if discrete:
        fig.update_xaxes(type='category')

    # Figure
    if save:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

def sorted_bar_chart(df, title, save=False, colors=combined_colors,col=None, sort_col=None, sort_list=True,
                      tickprefix=None, ticksuffix=None, font_size=18, remove_zero=False, custom_ticks=False,
                      bgcolor='rgba(0,0,0,0)', legend_orientation='h', bar_orientation='v', tickangle=None,
                      dtick=None, margin=dict(l=0, r=0, t=0, b=0), decimals=True, traceorder='normal',
                      tickformat=None, legend_placement=dict(x=0.01, y=1.1), legend_font_size=16, decimal_places=1,
                      barmode='stack', dimensions=dict(width=730, height=400), descending=True,show_legend=True,tick0=None,font_family=None,font_color='black',
                      file_type='svg',directory='../img',custom_annotation=[],buffer=None,ytick_num=6,
                      cumulative_sort=False, text=False,min_tick_spacing=125,
                    text_freq=1,text_position='outside',text_font_size=14, legend_background=dict(bgcolor='white',bordercolor='black',
                                                                                                    borderwidth=1, itemsizing='constant',
                                                                                                    yanchor="top",xanchor="center",buffer = 5),
                                                                                                                              autosize=True):
    # print(f'cumulative_sort: {cumulative_sort}')
    
    # print(f'sorted_bar_legend_orientation: {legend_orientation}')

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    space_buffer = " " * legend_background['buffer']

    combined_colors = colors

    if buffer != None:

        x_buffer = pd.Timedelta(days=buffer)
        x_range_start = df.index.min() - x_buffer
        x_range_end = df.index.max() + x_buffer
    
    else:
        x_range_start = df.index.min() 
        x_range_end = df.index.max() 

    # print(f'x_range_start:{x_range_start}')

    traces = []

    sort_list, color_map = rank_by_col(
        df=df, sort_col=sort_col, num_col=col, descending=descending,
        cumulative_sort=cumulative_sort, colors=colors
    )

    # print(f'df columns: {df.columns}')

    # print(f"sort_col: {sort_col}")
    # print(f"sort_list: {sort_list}")
    # print(f"df[sort_col]:\n{df[sort_col].unique()}")

    missing_values = set(sort_list) - set(df[sort_col].unique())
    # print(f"Missing values in sort_list: {missing_values}")

    # Iterate over sorted columns and assign colors accordingly
    for idx, i in enumerate(sort_list):
        i_df = df[df[sort_col] == i]

        color = color_map.get(i, colors[idx % len(colors)])

        if text and text_freq:
            # Create a list to hold text values based on the text frequency
            text_values = [
                f'{tickprefix if tickprefix else ""}'  # Add tickprefix
                f'{clean_values(i_df[col].iloc[i], decimal_places=decimal_places, decimals=decimals)}'  # Use .iloc for positional indexing
                f'{ticksuffix if ticksuffix else ""}'  # Add ticksuffix
                if i % text_freq == 0 else None for i in range(len(i_df))
            ]
              # Automatically adjust text position (inside/outside)
        else:
            text_values = ""

        # # Determine the color based on descending order
        # if descending:
        #     column_color = combined_colors[idx % len(combined_colors)]  # Normal order for descending
        # else:
        #     column_color = combined_colors[len(sort_list) - idx - 1]  # Reverse order for ascending

        # print(f'i_df:{i_df}')
        # print(f'col:{col}')
        # print(f'text font size: {text_font_size}')
        traces.append(go.Bar(
            x=i_df.index if bar_orientation == 'v' else i_df[col],
            y=i_df[col] if bar_orientation == 'v' else i_df.index,
            orientation=bar_orientation,
            showlegend=show_legend,
            text=text_values,
            textposition=text_position,
            name=f'{i} ({tickprefix if tickprefix else ""}{clean_values(i_df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places) if i_df.index.max() == df.index.max() else 0}{ticksuffix if ticksuffix else ""}){space_buffer}',
            marker=dict(color=color),
            textfont=dict(
                family=font_family,  # Use IBM Plex Mono font
                size=text_font_size,  # Set font size
                color="black"  # Set text color to black
            )
        ))

        if idx == 0:
            if custom_annotation:
                for date in custom_annotation:
                    if date in i_df.index:
                        y_value = i_df.loc[date, col]
                        annotation_text = f'{date}: {tickprefix if tickprefix else ""}{clean_values(y_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix if ticksuffix else ""}'

                        fig.add_annotation(dict(
                            x=date,
                            y=y_value,
                            text=annotation_text,
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1.5,
                            arrowwidth=1.5,
                            ax=-10,
                            ay=-50,
                            font=dict(size=16, family=font_family, color=font_color),
                            xref='x',
                            yref='y',
                            arrowcolor='black'  # Customize arrow color if needed
                        ))

    for trace in traces:
        fig.add_trace(trace, secondary_y=False)

    if custom_ticks:
        figy = df[col] 
        y_min = figy.min() if figy.min() < 0 else 0
        y_max = figy.max()
        ticksy = list(np.linspace(y_min, y_max, num=ytick_num, endpoint=True))

        #        Apply round_up_to_05 directly to each tick in ticksy
        ticksy = [round_up_to_05(tick) for tick in ticksy]

        if remove_zero:
            ticksy = [tick for tick in ticksy if tick != 0]
    else:
        ticksy = None  # Default to None if not using custom ticks

    # Convert datetime index to timestamps for linspace calculation
    # if pd.api.types.is_datetime64_any_dtype(df.index):
    #     # Default x_ticks and x_tick_labels
    #     x_ticks = None
    #     x_tick_labels = None

    #     unique_dates = df.index.drop_duplicates()
    #     total_periods = len(df.index)

    #     if total_periods > 3:
    #         # Number of desired ticks (adjustable)
    #         max_ticks = 10

    #         # Always include the first and last dates
    #         start = df.index.min()
    #         end = df.index.max()

    #         # Determine the step for even spacing
    #         step = max(1, (total_periods - 1) // (max_ticks - 1))

    #         # Calculate the tick indices
    #         tick_indices = list(range(0, total_periods, step))
    #         if (total_periods - 1) not in tick_indices:
    #             tick_indices.append(total_periods - 1)

    #         # Generate x_ticks and x_tick_labels
    #         x_ticks = [df.index[i] for i in tick_indices]
    #         x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in x_ticks]

    #         print("X-Ticks (Datetime):", x_ticks)
    #         print("X-Tick Labels:", x_tick_labels)

    #     else:
    #         # Fewer than 3 dates, show all
    #         x_ticks = unique_dates
    #         x_tick_labels = [tick.strftime('%Y-%m-%d') for tick in unique_dates]
    #         print("X-Ticks (Fewer than 3 Dates):", x_ticks)
    #         print("X-Tick Labels:", x_tick_labels)
    # else:
    #     x_ticks = None
    #     x_tick_labels = None

    x_ticks, x_tick_labels = generate_ticks_dynamic(df,dimensions['width'],min_tick_spacing)
    # print(f'x_ticks:{x_ticks}')

    fig.update_layout(
        barmode=barmode,
        autosize=autosize,
        legend=dict(
            orientation=legend_orientation,
            yanchor=legend_background['yanchor'],
            y=legend_placement['y'],  # Position above the plot area
            xanchor=legend_background['xanchor'],
            x=legend_placement['x'],  # Position to the left of the plot area
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor=legend_background['bgcolor'],
            bordercolor=legend_background['bordercolor'],
            borderwidth=legend_background['borderwidth'],
            traceorder=traceorder,
            itemsizing=legend_background['itemsizing']
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=text_font_size),  # Adjust minsize as needed
        font=dict(size=font_size, family=font_family, color=font_color),  # General font size, can be adjusted as needed
        width=dimensions['width'],
        height=dimensions['height'],  # Adjust as needed
        margin=margin
    )

    fig.update_layout(
        xaxis_title=dict(
            font=dict(size=font_size, family=font_family, color=font_color)
        ),
        xaxis=dict(
            range=[x_range_start, x_range_end],
            tickvals=x_ticks,
            tickangle=tickangle,
            tickfont=dict(size=font_size, family=font_family, color=font_color),
            dtick=dtick,
            tick0=tick0,
            tickformat=tickformat['x']
        ),
        yaxis=dict(
            tickvals=ticksy if custom_ticks else None,
            ticksuffix=ticksuffix,
            tickprefix=tickprefix,
            tickformat=tickformat['y1'],
            tickfont=dict(size=font_size, family=font_family, color=font_color)
        ),
    )

    if save:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

def pie_chart(df, sum_col, index_col, title, save=False,colors=combined_colors,bgcolor='rgba(0,0,0,0)',annotation_prefix=None, annotation_suffix = None, annotation_font_size=25,
              decimals=True,legend_font_size=16,font_size=18, legend_placement=dict(x=0.01,y=1.1),margin=dict(l=0, r=0, t=0, b=0),hole_size=.6,line_width=0,
              legend_orientation='v',decimal_places=1,itemsizing='constant',dimensions=dict(width=730,height=400),font_family=None,font_color='black',file_type='svg',directory='../img',textinfo='none',
              show_legend=False,text_font_size=12,text_font_color='black',texttemplate=None,annotation=True):
    
    original_labels = df[index_col].unique()
    # print(f'original_labels: {original_labels}')

    if textinfo == 'percent+label':
        percent=False
    else:
        percent=True
    
    df, total = to_percentage(df, sum_col, index_col,percent=percent)
    padded_labels = [f"{label}    " for label in df.index]

    # if textinfo == 'percent+label':
    #     labels = original_labels
    #     print(f'{textinfo}, {labels}')
    # else:
    labels = padded_labels
    # print(f'{textinfo}, {labels}')

    # print(f'textinfo: {textinfo}')

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=df[sum_col],
        hole=hole_size,
        textinfo=textinfo,
        showlegend=show_legend,
        texttemplate=texttemplate,  # Show label and value in the legend
        marker=dict(colors=colors, line=dict(color='white', width=line_width)),
        textfont=dict(
            family=font_family,
            size=text_font_size,
            color=text_font_color
        ),
        
    )])

    if annotation:
        annote = [dict(
            text=f'Total: {annotation_prefix if annotation_prefix else ""}{clean_values(total, decimals=decimals,decimal_places=decimal_places)}{annotation_suffix if annotation_suffix else ""}',  # Format the number with commas and a dollar sign
            x=0.5,  # Center horizontally
            y=0.5,  # Center vertically
            font=dict(
                size=annotation_font_size,  # Font size
                family=font_family,  # Font family with a bold variant
                color=font_color  # Font color
            ),
            showarrow=False,
            xref='paper',
            yref='paper',
            align='center'  # Center the text
        )]
    else:
        annote = None


    fig.update_layout(
        legend=dict(
            yanchor="top", 
            y=legend_placement['y'], 
            orientation=legend_orientation,
            xanchor="left", 
            x=legend_placement['x'],
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor='rgba(0,0,0,0)',
            itemsizing=itemsizing
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        margin=margin,
        autosize=True,
        font=dict(size=font_size, family=font_family),
        annotations=annote
    )

    # Adjust layout size
    fig.update_layout(
        width=dimensions['width'],
        height=dimensions['height'],  # Adjust as needed
        margin=margin
    )

    if save == True:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig
    
def bubble_chart(df, groupby, num_col, keep_topn=False, other=False, topn=10, title='l1_fdv_cluster',
                 scaling=dict(marker_scale=2e10), seed=42, use_physics=True,marker_col=None,show_text=True,
                 show_legend=False, marker=dict(sizemin=10, mode="markers+text", opacity=1),
                 text=dict(general=18, annotation=18), annotation_dict=dict(yshift=-20), groupby_color=None, scale_y=False,x_num_col=None,rescale=False,
                    tickprefix=None,ticksuffix=None,exclude_largest=False,save=False,dimensions=dict(w=730,h=351),
                    margin_modifier = 25,colors=combined_colors,flat_line=False,x_tickvals=None, x_ticktext=None):
    
    combined_colors = colors
    
    x_tickprefix, x_ticksuffix = None, None
    y_tickprefix, y_ticksuffix = None, None

    # print(f'num_col at start: {num_col}')

    # print(f'marker: {marker}')
    
    if num_col == 'market_cap':
        y_tickprefix = '$'
    elif num_col == 'market_cap_change_percentage_24h':
        y_ticksuffix = '%'

    # Set x-axis prefix and suffix based on x_num_col
    if x_num_col == 'market_cap':
        x_tickprefix = '$'
    elif x_num_col == 'market_cap_change_percentage_24h':
        x_ticksuffix = '%'

    # if x_num_col is not None:
    #     # Ensure there are no zero or negative values before applying log
    #     df = df[df[x_num_col] > 0]
        
    #     # Apply the natural logarithm to the x_num_col values
    #     df[x_num_col] = np.log(df[x_num_col])

    #     # Set x_values to the transformed x_num_col
    #     x_values = df[x_num_col]
    # else:
    #     x_values = range(len(df))
    
    print("\n=== Initial DataFrame ===")
    print(df)

    original_df = df.copy()

    print(f'num_col: {num_col}')

    print(f'other: {keep_topn}')

    # Handle top N filtering if specified
    if keep_topn:
        if other:
            df = top_other_by_col_bubble(df=df, sort_col=groupby, sum_col=num_col, num=topn, groupby_color=groupby_color)
        else:
            df = top_by_col_bubble(df=df, sort_col=groupby, sum_col=num_col, num=topn, groupby_color=groupby_color)
        print("\n=== DataFrame After Top N Filtering ===")
        print(f'df bf if groupby_color: {df[groupby].unique()}')
        print(df)
    print(f'num_col: {num_col}')

    num_points = len(df[groupby].unique())
    dynamic_k = 1 / (num_points ** 0.5)  # Adjust the exponent to control spread
    dynamic_iterations = min(max(num_points * 10, 200), 2000)  # Between 200 and 2000

    # Drop NaN values for groupby and num_col
    df = df.dropna(subset=[groupby, num_col])

    if exclude_largest:
        max_index = df[num_col].idxmax()
        df = df.drop(max_index)
        print("\n=== DataFrame After Excluding Largest Datapoint ===")
        print(df)

    if rescale:
    
        params = dynamic_parameters(df, num_col=num_col)
        print(f'params: {params}')

        # Proceed with the rest of the function as usual
        scaling['marker_scale'] = params['dynamic_marker_scale']

    # Initialize group_cols with groupby
    group_cols = [groupby]
    
    # Add 'id' and 'symbol' if they exist in the DataFrame
    if 'id' in df.columns:
        group_cols.append('id')
    if 'symbol' in df.columns:
        group_cols.append('symbol')
    
    # Add groupby_color if it's specified and not the same as groupby
    if groupby_color and groupby_color != groupby:
        group_cols.append(groupby_color)
    
    # Ensure unique values while preserving order
    group_cols = list(dict.fromkeys(group_cols))
    
    # Group by the dynamically created group_cols and sum num_col
        # Drop NaN values for groupby, num_col, and x_num_col if specified
    subset_cols = [groupby, num_col]
    if x_num_col is not None:
        subset_cols.append(x_num_col)

    # df = df.dropna(subset=subset_cols)

    # Group by the dynamically created group_cols and aggregate num_col and x_num_col
    agg_dict = {num_col: 'sum'}
    if x_num_col:
        agg_dict[x_num_col] = 'mean'  # Use 'mean' or any other appropriate aggregation function
    
    if marker_col is not None:
        group_cols.append(marker_col)

    df = df.groupby(group_cols).agg(agg_dict).reset_index()

    df.fillna(0,inplace=True)

    print("\n=== DataFrame After Dropping NaNs ===")
    print(df)

    if x_num_col is None:
        x_values = range(len(df))
    else:
        x_values = df[x_num_col]

    # Create positions DataFrame
    if use_physics:
    # Create a graph and add nodes with attributes (size based on num_col)
        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_node(tuple(row[group_cols]), size=row[num_col])
    
        print("\n=== Nodes in Graph ===")
        print(G.nodes)
    
        # Add arbitrary edges to simulate clustering
        for i in range(len(df)):
            for j in range(i + 1, len(df)):
                G.add_edge(tuple(df.iloc[i][group_cols]), tuple(df.iloc[j][group_cols]))
    
        # Compute positions using a force-directed layout
        positions = nx.spring_layout(G, seed=seed, k=dynamic_k, iterations=dynamic_iterations)
    
        print("\n=== Positions Computed ===")
        print(positions)
    
        # Extract positions into a DataFrame
        pos_df = pd.DataFrame({
            **{col: [key[i] for key in positions.keys()] for i, col in enumerate(group_cols)},
            "x": [p[0] for p in positions.values()],
            "y": [p[1] for p in positions.values()],
            num_col: [G.nodes[n]["size"] for n in positions.keys()],
        })
    elif flat_line:
        df = df.sort_values(by=num_col, ascending=False).reset_index(drop=True)

        # Assign sequential x-values and a fixed y-value
        df["x"] = range(len(df))
        df["y"] = 0

        pos_df = df.copy()
    
    else:
        # Regular bubble chart: use sequential positions for x and y scaled to num_col
        pos_df = df.copy()
        pos_df["x"] = x_values
        pos_df["y"] = df[num_col]
        if scale_y:
            max_y = df[num_col].max()
            min_y = df[num_col].min()
            pos_df["y"] = (df[num_col] - min_y) / (max_y - min_y) * 100  # Scale y to a range of 0 to 100

    if groupby_color is None:
        groupby_color = groupby

     # Calculate summed values for legend
    legend_sums = df.groupby(groupby_color)[num_col].sum().reset_index().sort_values(by=num_col, ascending=False)
    print(f'legend_sums: {legend_sums}')
    print(f'num_col: {num_col}')
    legend_sums[num_col] = legend_sums[num_col].apply(clean_values)

    # Create a color map for groupby_color
    unique_categories = pos_df[groupby_color].unique()

    group_sums = pos_df.groupby(groupby_color)[num_col].sum()
    sorted_groups = group_sums.sort_values(ascending=False).index

    category_color_map = {
        category: combined_colors[0] if idx == 0 else combined_colors[(idx + 1) % len(combined_colors)]
        for idx, category in enumerate(sorted_groups)
    }
    print(f'category_color_map: {category_color_map}')

    largest_y_per_category = pos_df.groupby(groupby_color)[num_col].idxmax()

    categories_in_legend = set()

    print("\n=== Positions DataFrame ===")
    print(pos_df)

    # Create the Plotly figure
    fig = go.Figure()

    if groupby_color:
        # Calculate the total sum for each category and sort by descending order
        group_sums = pos_df.groupby(groupby_color)[num_col].sum()
        sorted_categories = group_sums.sort_values(ascending=False).index

        # Create the category color map based on the sorted categories
        category_color_map = {
            category: combined_colors[idx % len(combined_colors)]
            for idx, category in enumerate(sorted_categories)
        }

        print(f'category_color_map: {category_color_map}')

    # Track which categories have already been added to the legend
    categories_in_legend = set()

    print(f'pos_df: {pos_df}')

    # Add each node as a scatter point and assign colors
    for idx, (_, row) in enumerate(pos_df.iterrows()):
        # Determine the color based on the category
        print(F'groupby_color, groupby, color: {row[groupby_color], row[groupby]}, {category_color_map[row[groupby_color]]}')
        color = category_color_map.get(row[groupby_color], combined_colors[idx % len(combined_colors)]) if groupby_color else combined_colors[idx % len(combined_colors)]
        legend_sum = group_sums.get(row[groupby_color], 0)
        print(f'at color after legend_sum: {color}')
        print(f'show_text: {show_text}')
        if show_text:
            trace_name = f"{row[groupby_color]} ({tickprefix if tickprefix else ''}{legend_sum}{ticksuffix if ticksuffix else ''})"
        else:
            trace_name = None

        show_legend_entry = idx in largest_y_per_category.values and row[groupby_color] not in categories_in_legend
        # print(f'largest_y_per_category[idx]:{largest_y_per_category[idx]}')
        print(f'show_legend_entry:{show_legend_entry}')
        print(f'categories_in_legend:{categories_in_legend}')
        if show_legend_entry:
            categories_in_legend.add(row[groupby_color])

        print(f'pos_df: {pos_df.columns}')


        # Create hyperlink text if 'id' is in the DataFrame columns
        if 'id' in pos_df.columns:
            if 'symbol' in pos_df.columns:
                text_wording = (
                    f'<a href="https://www.coingecko.com/en/coins/{row["id"]}" target="_blank">{row["symbol"]}</a>'
                    f'<br>${clean_values(row[num_col], decimals=True, decimal_places=1)}'
                )
            else:
                text_wording = (
                    f'<a href="https://www.coingecko.com/en/coins/{row["id"]}" target="_blank">{row["symbol"]}</a>'
                    f'<br>${clean_values(row[num_col], decimals=True, decimal_places=1)}'
                )

        else:
            text_wording = None

        # Show legend only once per category
        if groupby_color and row[groupby_color] not in categories_in_legend:
            categories_in_legend.add(row[groupby_color])
        
        if marker_col is not None:
            marker_size_col = marker_col
        else:
            marker_size_col = num_col

        print(f'row[marker_size_col]: {row[marker_size_col]}')

        size = calculate_marker_size(row[marker_size_col], scaling['marker_scale'])
        if size <= 0:
            size = marker['sizemin']*5  # Use the minimum marker size as a fallback

        print(f' at trace color for {row[groupby_color]}, {row[groupby]}: {color}')
        print(f'sizemin: {marker["sizemin"]}')

        print(f'trace_name: {trace_name}, text_wording: {text_wording}')

        print(f'size: {size}')

        fig.add_trace(
            go.Scatter(
                x=[row["x"]],
                y=[row["y"]],
                mode=marker['mode'],
                marker=dict(
                    size=size,
                    sizemode="area",
                    sizemin=marker['sizemin'],
                    opacity=marker['opacity'],
                    color=color,
                ),
                text=text_wording,
                name=trace_name,
                showlegend = False
            )
        )

        if 'id' not in pos_df.columns:
            if show_text==True:

                # Add annotation for the FDV value above the data point
                fig.add_annotation(
                    x=row["x"],
                    y=row["y"],
                    text=f"{row[groupby]}<br>${clean_values(row[num_col], decimals=True, decimal_places=1)}",
                    showarrow=False,
                    font=dict(size=text['annotation'], color='black'),
                    yshift=annotation_dict['yshift']
                )
            else:
                # Add annotation for the FDV value above the data point
                fig.add_annotation(
                    x=row["x"],
                    y=row["y"],
                    text=f"{row[groupby]}",
                    showarrow=False,
                    font=dict(size=text['annotation'], color='black'),
                    yshift=annotation_dict['yshift']
                )

    if show_legend:

        legend_marker_size = 20  # Fixed size for legend markers
        for _, row in legend_sums.iterrows():
            trace_name = f"{row[groupby_color]} (${row[num_col]})"
            color = category_color_map[row[groupby_color]]
        
            fig.add_trace(
                go.Scatter(
                    x=[None],  # No data point; used only for the legend
                    y=[None],
                    mode=marker['mode'],
                    marker=dict(
                        size=legend_marker_size,
                        sizemin=marker['sizemin'],
                        sizemode="area",
                        opacity=marker['opacity'],
                        color=color,
                    ),
                    name=trace_name,
                    showlegend=True
                )
            )

    index_length = len(df.index)

    if x_num_col is not None:
        if x_tickvals is None or x_ticktext is None:
            x_tickvals = None
            x_ticktext = None
    else:
        x_tickvals = list(range(index_length))
        x_ticktext = [""] * index_length

    if use_physics:
        # Axes configuration for physics-based layout
        fig.update_layout(
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                tickvals=list(range(index_length)), 
                ticktext=[""] * index_length
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                tickvals=list(range(index_length)), 
                ticktext=[""] * index_length
            )
        )
    elif flat_line:
        fig.update_layout(
            xaxis=dict(
                showgrid=False, 
                zeroline=False,
                tickvals=list(range(index_length)), 
                ticktext=[""] * index_length
                # title=x_num_col.replace('_',' ').title() if x_num_col is not None else None
            ),
            yaxis=dict(
                showgrid=True, 
                zeroline=True,
                tickvals=list(range(index_length)), 
                ticktext=[""] * index_length
                # title=num_col.replace('_',' ').title()
            )
        )
    else:
        # Axes configuration for non-physics layout with meaningful values
        fig.update_layout(
            xaxis=dict(
                showgrid=False, 
                zeroline=False,
                tickvals=x_tickvals, 
                ticktext=x_ticktext,
                tickprefix=x_tickprefix,
                ticksuffix=x_ticksuffix,
                title=x_num_col.replace('_',' ').title() if x_num_col is not None else None
            ),
            yaxis=dict(
                showgrid=True, 
                zeroline=True,
                tickprefix=y_tickprefix,
                ticksuffix=y_ticksuffix,
                title=num_col.replace('_',' ').title()
            )
        )

    margin_t = margin_modifier if show_legend else 0

    # Update layout for better aesthetics
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=text['general'], family="IBM Plex Mono", color="black"),
        margin=dict(t=margin_t, b=0, l=0, r=0),
        legend=dict(
            orientation='v',
            x=0.9,
            y=0.5,
            font=dict(size=12),
            xanchor="left",         # Anchor the legend to the left
            yanchor="bottom",
        ),
        width=dimensions['w'],
        height=dimensions['h'],  # Adjust as needed
    )

    if save:
        pio.write_image(fig, f'{title}.svg')

    # Display the figure
    return fig

def ranked_line_chart(df, title, save=False, colors=combined_colors, barmode='stack', col=None, sort_col=None,
                     tickprefix=None, ticksuffix=None, font_size=18,
                     bgcolor='rgba(0,0,0,0)', legend_orientation='h', tickangle=None, textposition="outside", orientation="h",
                     legend_placement=dict(x=0.01, y=1.1), minsize=16, legend_font_size=16, margin=dict(l=0, r=0, t=0, b=0),
                     showlegend=False, decimals=True, traceorder='normal', decimal_places=1, to_reverse=False,
                     tickformat=',.0f', itemsizing='constant', trace_text=14, dimensions=dict(width=730, height=400), descending=True,
                     use_sort_list=True,show_text=True,font_family=None,font_color='black',file_type='svg',directory='../img',
                     use_single_color=False,discrete=False):

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    combined_colors = colors

    primary_color = colors[0] if use_single_color else None

    print(f'combined_colors: {combined_colors}')
    print(f'primary_color: {primary_color}')

    traces = []
    print(f'df sort order before ranked cleaning: {df[sort_col].unique()}')

    df, sort_list = ranked_cleaning(df, col, sort_col, descending=descending,use_sort_list=use_sort_list)
    print(f'df: {df}')

    print(f'Decimal Places: {decimal_places}')

    # if use_sort_list:
    #     sort_list = sort_list
    # else:
    #     sort_list = df.columns

    print(f'sort_list: {sort_list}')

    if to_reverse:
        sort_list = reversed(sort_list)

    print(f'sort list: {sort_list}')
    for idx, i in enumerate(sort_list):
        if showlegend:
            print(f'i: {i} \nidx: {idx} \nprefix: {ticksuffix}')
            name = f'{i} ({tickprefix if tickprefix else ""}{clean_values(df[df[sort_col] == i][col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix if ticksuffix else ""}){"                  "}' 
            text = None
            y = idx
        else:
            if show_text:
                print(f'i: {i} \nidx: {idx} \nprefix: {ticksuffix}')
                name = None
                # Add buffer (spaces) at the end of each formatted text value
                text = df[df[sort_col] == i][col].apply(
                    lambda x: f'{tickprefix if tickprefix else ""}{clean_values(x, decimals=decimals, decimal_places=decimal_places)}{ticksuffix if ticksuffix else ""}'
                )
                y = i
            else:
                print(f'i: {i} \nidx: {idx} \nprefix: {ticksuffix}')
                name = None
                text = None
                y = i


        print(f'idx: {idx} i: {i}')

        # Determine the color based on descending order
        if use_single_color:
            color = primary_color  # Use the first color in the list
        elif descending:
            color = combined_colors[idx % len(combined_colors)]  # Normal order for descending
        else:
            color = combined_colors[len(sort_list) - idx - 1]  # Reverse order for ascending

        print(f'use_single_color:{use_single_color}')
        print(f'color: {color}')

        if orientation == 'v':  # Vertical orientation
            x = [i]  # Categorical value on the x-axis
            y = df[df[sort_col] == i][col]  # Numeric value on the y-axis
        else:  # Horizontal orientation
            x = df[df[sort_col] == i][col]
            y = [i]  # Categorical value on the y-axis

        traces.append(go.Scatter(
            y=y,
            x=x,
            orientation=orientation,
            line=dict(color=color, width=7),
            text=text,
            mode='lines',
            textfont=dict(size=trace_text, color=font_color),  # Change this to adjust font size
            textposition=textposition,
            name=name,
            marker=dict(color=color),
            showlegend=showlegend
        ))

    for trace in traces:
        fig.add_trace(trace, secondary_y=False)

    fig.update_layout(
        barmode=barmode,
        autosize=True,
        legend=dict(
            orientation=legend_orientation,
            yanchor="top",
            y=legend_placement['y'],  # Position above the plot area
            xanchor="left",
            x=legend_placement['x'],  # Position to the left of the plot area
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor='rgba(0,0,0,0)',  # Make the legend background transparent
            traceorder=traceorder,
            itemsizing=itemsizing
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=minsize),  # Adjust minsize as needed
        font=dict(size=font_size, family=font_family, color=font_color),  # General font size, can be adjusted as needed
    )

    # Adjust layout size
    fig.update_layout(
        width=dimensions['width'],
        height=dimensions['height'],  # Adjust as needed
        margin=margin
    )

    index_length = len(df.index)

    print(f'text: {show_text}')

    if orientation == 'v':
        xtickangle = tickangle
        ytickangle = 0
        if not showlegend:
            ytickprefix = tickprefix
            yticksuffix = ticksuffix
            xtickprefix = None  # No prefix for x-axis if legend is not shown
            xticksuffix = None  # No suffix for x-axis if legend is not shown

            if show_text:
                ticktext = list(range(index_length)) 
                tickvals = [""] * index_length
            else:
                ticktext = None
                tickvals = None
            
        else:
            ytickprefix = tickprefix
            yticksuffix = ticksuffix
            tickvals = list(range(index_length))  # Tick values based on index length for y-axis
            ticktext = [""] * index_length  # No specific ticktext if showing legend
            xtickprefix = None  # Adjust if needed based on your requirements
            xticksuffix = None  # Adjust if needed based on your requirements
        
        xtickvals = None
        xticktext = None

    else:  # Horizontal orientation
        xtickangle = 0
        ytickangle = tickangle
        if not showlegend:
            print(f'no legend, horizontal')
            ytickprefix = None
            yticksuffix = None
            tickvals = None  # No specific tick values for y-axis
            ticktext = [""] * index_length  # Empty strings for tick labels on the y-axis
            xtickprefix = tickprefix  # Use tickprefix for x-axis if not showing legend
            xticksuffix = ticksuffix  # Use ticksuffix for x-axis if not showing legend

            if show_text:
                xtickvals = list(range(index_length)) 
                xticktext = [""] * index_length
            else:
                xtickvals = None
                xticktext = None

        else:
            print(f'legend, horizontal')
            ytickprefix = None
            yticksuffix = None
            tickvals = list(range(index_length))  # No specific tick values for y-axis
            ticktext = [""] * index_length  # No specific ticktext if showing legend
            xtickprefix = tickprefix  # Use tickprefix for x-axis if showing legend
            xticksuffix = ticksuffix  # Use ticksuffix for x-axis if showing legend

    # print(f'ytickvals: {tickvals}')
    # print(f'yticktext: {ticktext}')
    # print(f'ytickprefix: {ytickprefix}')
    # print(f'xtickprefix: {xtickprefix}')
    # print(f'xtickvals: {xtickvals if xtickvals else ""}')
    # print(f'xticktext: {xticktext if xtickvals else ""}')

    fig.update_layout(
        xaxis_title=dict(
            font=dict(size=font_size, family=font_family, color=font_color),
        ),
        xaxis=dict(tickangle=xtickangle,
                   tickfont=dict(size=font_size, family=font_family, color=font_color),
                   tickprefix=xtickprefix,
                   ticksuffix=xticksuffix,
                   tickformat=tickformat,
                   tickvals=xtickvals,
                   ticktext=xticktext
                   ),

        yaxis=dict(tickprefix=ytickprefix,
                   ticksuffix=yticksuffix,
                   tickangle=ytickangle,
                   tickfont=dict(size=font_size, family=font_family, color=font_color),
                   tickvals=tickvals,  # Set tick values to blank if not showing legend
                   ticktext=ticktext),
        
        
                   

    )

    if discrete:
        fig.update_xaxes(type='category')

    # Figure
    if save:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

def create_heatmap(
    df,
    x_col,
    y_col,
    z_col,
    width=800,
    height=500,
    title="Heatmap",
    xaxis_title=None,
    yaxis_title=None,
    color_base="#1f77b4",  # Default blue
    font_size=12,
    legend_font_size=10,
    tick_font_color="#333",
    tick_suffix="",
    margins=dict(t=50, b=50, l=50, r=50),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    show=True,
    save=True
):
    # Generate custom 2-color colorscale from base color
    colorscale = [
        [0, "white"],
        [1, color_base]
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=df[z_col],
            x=df[x_col],
            y=df[y_col],
            colorscale=colorscale,
            colorbar=dict(
                title=z_col.replace("_", " ").title(),
                tickfont=dict(size=legend_font_size, color=tick_font_color),
                titlefont=dict(size=legend_font_size, color=tick_font_color)
            )
        )
    )

    fig.update_layout(
        title=title,
        width=width,
        height=height,
        xaxis_title=xaxis_title or x_col.replace("_", " ").title(),
        yaxis_title=yaxis_title or y_col.replace("_", " ").title(),
        font=dict(size=font_size, color=tick_font_color),
        margin=margins,
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=paper_bgcolor,
    )

    fig.update_xaxes(ticksuffix=tick_suffix)

    if show:
        fig.show()

    if save == True:
        pio.write_image(fig, 'heatmap.svg', engine="kaleido")

    return fig
