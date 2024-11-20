import sys

# sys.path.append('E:\Projects\ournetwork\chart_builder\scripts')  
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

import math

# sys.path.append(os.path.join(current_dir, 'pipeline', 'scripts'))

print("Current working directory:", os.getcwd())
print("Current directory:", current_dir)

from chart_builder.scripts.utils import colors, clean_values, clean_values_dollars, ranked_cleaning, to_percentage, rank_by_col, rank_by_columns, normalize_to_percent 

import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import plotly.offline as pyo
import plotly.colors as pc
# import kaleido

import pandas as pd

combined_colors = colors()

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

def simple_line_plot(df, title, axes_titles=dict(y1=None, y2=None),color_options=None, mode='lines', area=False, annotations=True, tickprefix=dict(y1=None,y2=None), 
                     ticksuffix=dict(y1=None,y2=None), remove_zero=False, custom_ticks=False,
                      colors=combined_colors, font_size=18, axes_data=dict(y1=None,y2=None), 
                     bgcolor='rgba(0,0,0,0)', legend_orientation='h', tickangle=None, show_legend=False,
                     sort_list=True, dtick=None, max_annotation=False, tickformat=None, tick0=None,
                     traceorder='normal', legend_placement=dict(x=0.01,y=1.1), margin=dict(l=0, r=0, t=0, b=0), legend_font_size=16,
                     line_width=4, marker_size=10,cumulative_sort=False,decimal_places=1,decimals=True,dimensions=dict(width=730,height=400),
                     save=False,fill=None,connectgaps=True,descending=True,text=False,text_freq=1,font_family=None,font_color='black',axes_font_colors=None,
                     file_type='svg',directory='../img',
                     custom_annotation=[],ytick_num=6,auto_title=False,buffer=None):

    "custom_annotation is an array of dates we want annotations for value"

    print(f'tick0 in func: {tick0}')

    if bgcolor == 'default':
        bgcolor = 'rgba(0,0,0,0)'
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    color_order = rank_by_columns(df, cumulative=True, descending=True)
    
    # Determine plotting order based on the latest value
    plot_order = rank_by_columns(df, cumulative=False, descending=descending)

    print(f"Color order (cumulative): {color_order}")
    print(f"Plot order (latest value): {plot_order}")

    color_map = {col: colors[idx % len(colors)] for idx, col in enumerate(color_order)}

    y1_lineto_show = None
    y2_lineto_show = None

    print(f'axes_titles at beginning: {axes_titles}')

    if buffer != None:

        x_buffer = pd.Timedelta(days=buffer)
        x_range_start = df.index.min() - x_buffer
        x_range_end = df.index.max() + x_buffer
    
    else:
        x_range_start = df.index.min() 
        x_range_end = df.index.max()  

    print(f'cumulative_sort: {cumulative_sort}')
  
    # Sort columns by descending or ascending
    # sort_list = rank_by_columns(df=df, cumulative=cumulative_sort, descending=descending)
    columns_to_plot = plot_order

    # Print for debugging
    print(f"descending: {descending}")
    print(f"columns to plot: {columns_to_plot}")

    
    if axes_font_colors == 'auto' or axes_font_colors is None:
        axes_font_colors = {}

    traces = []

    y1_lineto_show = df[axes_data['y1'][0]].name if auto_title and not axes_titles['y1'] else axes_titles['y1']
    y2_lineto_show = df[axes_data['y2'][0]].name if auto_title and not axes_titles['y2'] else axes_titles['y2']
    
    print(f'axes_font_colors: {axes_font_colors}')

    # Loop through the y1 columns, applying sorted order
    for idx, y1_col in enumerate(columns_to_plot):
        print(f'idx: {idx} y1_col: {y1_col}')
        if y1_col not in axes_data['y1']:
            continue  # Skip if y1_col is not in the sorted columns

        print(f'axes_titles: {axes_titles}')
        
        print(f'y1_lineto_show: {y1_lineto_show}')
        
        # Assign colors based on position: reverse for ascending
        print(f'colors: {colors}')
        if descending:
            column_color = colors[idx % len(colors)]  # Normal order for descending
        else:
            column_color = colors[len(columns_to_plot) - idx - 1]  # Reverse order for ascending

        if 'y1' not in axes_font_colors:
            axes_font_colors['y1'] = column_color

        print(f'axes_font_colors: {axes_font_colors}')

        print(f'Processing y1 column: {y1_col} with color: {column_color}')  # Debugging info

        print(f'latest val: {df[y1_col].iloc[-1]}')

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
        
        print(f'column_color: {column_color}')

        print(f'y1_col values:{df[y1_col]} ')

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[y1_col],
            mode=mode,
            text=text_values,
            name=f'{y1_col} ({tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""})',
            stackgroup=None if area == False else 'one',
            line=dict(color=color_map[y1_col], width=line_width),
            marker=dict(color=column_color, size=marker_size), 
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
        last_text = f'{df.index[-1].strftime("%m-%d-%Y")}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
    else:
        last_text = f'{df.index[-1]}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

    # Handling the first value annotation
    if datetime_tick:
        first_text = f'{df.index[0].strftime("%m-%d-%Y")}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[0], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
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
            font=dict(size=16, family=font_family, color=font_color),
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
            font=dict(size=16, family=font_family, color=font_color),
            xref='x',
            yref='y',
            arrowcolor='black'
        ))

    # Handling the maximum value annotation
    if max_annotation:
        max_value = df[y1_col].max()
        max_index = df[df[y1_col] == max_value].index[0]  # Get the index where the maximum value occurs

        if datetime_tick:
            max_text = f'{max_index.strftime("%m-%d-%Y")}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(max_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""} (ATH)'
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
            font=dict(size=16, family=font_family, color=font_color),
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
                    font=dict(size=16, family=font_family, color=font_color),
                    xref='x',
                    yref='y',
                    arrowcolor='black'  # Customize arrow color if needed
                ))

    # Check for y2 columns, applying sorted order as well
    if axes_data['y2']:
        print(f'axes_data y2: {axes_data["y2"]}')
        print(f'columns_to_plot: {columns_to_plot}')
        for idx, y2_col in enumerate(columns_to_plot):
            if y2_col not in axes_data["y2"]:
                print(f'Skipping y2 column: {y2_col} (not in columns to plot)')
                continue
            if y2_col not in columns_to_plot:
                continue  # Skip if y2_col is not in the sorted columns

            print(f'idx: {idx} y2_col: {y2_col}')

            print(f'line to show 2: {y2_lineto_show}')

            # Assign colors based on position: reverse for ascending
            if descending:
                column_color = colors[idx % len(colors)]  # Normal order for descending
            else:
                column_color = colors[len(columns_to_plot) - idx - 1]  # Reverse order for ascending

            if 'y2' not in axes_font_colors:
                axes_font_colors['y2'] = column_color
          
            print(f'Processing y2 column: {y2_col} with color: {column_color}') 
            
            print(f'y2_col values:{df[y2_col]} ') # Debugging info

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[y2_col],
                mode=mode,
                name=f'{y2_col} ({tickprefix["y2"] if tickprefix["y2"] else ""}{clean_values(df[y2_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y2"] if ticksuffix["y2"] else ""})' + "     ",
                stackgroup=None if area == False else 'one',
                line=dict(color=column_color, width=line_width),
                marker=dict(color=column_color, size=marker_size), 
                showlegend=show_legend,
                connectgaps=connectgaps,
                fill=fill
            ), secondary_y=True)

    print(f'axes_font_colors: {axes_font_colors}')

    if custom_ticks:
        y_min = df[axes_data["y1"]].min().min() if df[axes_data["y1"]].min().min() < 0 else 0
        y_max = df[axes_data["y1"]].max().max()

        print(f'y_min: {y_min}')
        print(f'y_max: {y_max}')
        
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
    
    print(f'ticksy: {ticksy}')

    print(f'[x_range_start, x_range_end]: {[x_range_start, x_range_end]}')


    if pd.api.types.is_datetime64_any_dtype(df.index):
        x_start = df.index.min().timestamp()
        x_end = df.index.max().timestamp()
        x_ticks_numeric = np.linspace(x_start, x_end, num=5)
        x_ticks = [pd.to_datetime(tick, unit='s').strftime('%Y-%m-%d') for tick in x_ticks_numeric]
    else:
        x_ticks = None

    fig.update_layout(
        legend=dict(
            orientation=legend_orientation,
            yanchor="top",
            y=legend_placement['y'],
            xanchor="left",
            x=legend_placement['x'],
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor='rgba(0,0,0,0)',
            traceorder=traceorder,
            itemsizing='constant'
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=15),
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
            tick0=tick0
        ),
        yaxis=dict(
            tickfont=dict(size=font_size, family=font_family, color=axes_font_colors.get("y1", font_color)),
            ticksuffix=ticksuffix.get("y1", ""),
            tickprefix=tickprefix.get("y1", ""),
            tickformat=tickformat.get("y1", ""),
        ),
        yaxis2=dict(
            tickfont=dict(size=font_size, family=font_family, color=axes_font_colors.get("y2", font_color)),
            overlaying='y',
            ticksuffix=ticksuffix.get("y2", ""),
            tickprefix=tickprefix.get("y2", ""),
            tickformat=tickformat.get("y2", "")
        )
    )

    # Figure
    # pyo.iplot(fig)
    if save == True:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

    # return fig

def simple_bar_plot(df, title, save=False, color_options=None, annotations=True,
                    colors=combined_colors, font_size=18, remove_zero=False, custom_ticks=False,
                    bgcolor='rgba(0,0,0,0)', legend_orientation='h', tickangle=None, show_legend=False,
                    dtick=None, max_annotation=False, tick0=None, traceorder='normal',
                    legend_placement=dict(x=0.01, y=1.1), margin=dict(l=0, r=0, t=0, b=0), legend_font_size=16, decimals=True,
                    custom_tickval=None, custom_ticktext=None, xtick_prefix=None,
                    cumulative_sort=False, decimal_places=1, barmode='stack', text=False,
                    text_freq=1, text_font_size=12, dimensions=dict(width=730, height=400), rangebreaks=None, text_position='outside',
                    axes_data=dict(y1=None, y2=None), tickformat=dict(x=None, y1=None, y2=None), axes_titles=dict(y1=None, y2=None),
                    tickprefix=dict(y1=None, y2=None), ticksuffix=dict(y1=None, y2=None), descending=True,datetime_tick=True,font_family=None,font_color='black',file_type='svg',
                    directory='../img',custom_annotation=[],buffer=None,ytick_num=6, auto_title=True):
    print(f'testing')
    print(f'axes_data:{axes_data}')
    if bgcolor == 'default':
        bgcolor = 'rgba(0,0,0,0)'
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    y1_lineto_show = None
    y2_lineto_show = None



    if buffer != None:

        x_buffer = pd.Timedelta(days=buffer)
        x_range_start = df.index.min() - x_buffer
        x_range_end = df.index.max() + x_buffer
    
    else:
        x_range_start = df.index.min() 
        x_range_end = df.index.max() 

    
    # Sort columns by descending or ascending
    sort_list = rank_by_columns(df=df, cumulative=cumulative_sort, descending=descending)
    columns_to_plot = sort_list
    
    # Print for debugging
    print(f"descending: {descending}")
    print(f"columns to plot: {columns_to_plot}")
    print(f'tick0: {tick0}')

    # tick0 = df.index.min()

    # print(f'new tick0: {tick0}')
    
    # Assign colors based on position (last-ranked gets the first color in reversed list)
    # Assign colors based on position (last-ranked gets the first color in reversed list)
    for idx, y1_col in enumerate(columns_to_plot):
        print(f'idx: {idx}, y: {y1_col}')
        if y1_col not in axes_data["y1"]:
            continue  # Skip if the column isn't in the sorted list

        if auto_title == True:
            y1_lineto_show = y1_col if axes_titles["y1"] == None else axes_titles["y1"]
        elif auto_title == False:
            y1_lineto_show = axes_titles["y1"]

        print(F'auto_title: {auto_title}')
        print(F'y1_lineto_show: {y1_lineto_show}')
        # Assign colors based on position: reverse for ascending
        if descending:
            column_color = colors[idx % len(colors)]  # Normal order for descending
        else:
            column_color = colors[len(columns_to_plot) - idx - 1]  # Reverse order for ascending
            
        print(f"Processing y1 column: {y1_col} with color: {column_color}")  # Debugging info

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

        print(f'index: {df.index}')
        print(f'vals: {df[y1_col]}')
      
        # Add the trace for each y1 column with the color assignment
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[y1_col],
            name=f'{y1_col} ({tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""})',
            marker=dict(color=column_color),
            text=text_values,  # Use the filtered text values based on frequency
            textposition=text_position,  # Position of the text on the bars
            showlegend=show_legend,
            textfont=dict(
                family=font_family,  # Use IBM Plex Mono font
                size=text_font_size,  # Set font size
                color="black"  # Set text color to black
            )
        ), secondary_y=False)

        print(f'datetime_tick: {datetime_tick}')

        # if pd.api.types.is_datetime64_any_dtype(df.index):
        #     datetime_tick = True
        # else:
        #     datetime_tick = False

        # Handling the last value annotation
        if datetime_tick:
            last_text = f'{df.index[-1].strftime("%m-%d-%Y")}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
        else:
            last_text = f'{df.index[-1]}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

        # Handling the first value annotation
        if datetime_tick:
            first_text = f'{df.index[0].strftime("%m-%d-%Y")}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[y1_col].iloc[0], decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'
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
                font=dict(size=16, family=font_family, color=font_color),
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
                font=dict(size=16, family=font_family, color=font_color),
                xref='x',
                yref='y',
                arrowcolor='black'
            ))

        # Handling the maximum value annotation
        if max_annotation:
            max_value = df[y1_col].max()
            max_index = df[df[y1_col] == max_value].index[0]  # Get the index where the maximum value occurs

            if datetime_tick:
                max_text = f'{max_index.strftime("%m-%d-%Y")}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(max_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""} (ATH)'
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
                font=dict(size=16, family=font_family, color=font_color),
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
                        font=dict(size=16, family=font_family, color=font_color),
                        xref='x',
                        yref='y',
                        arrowcolor='black'  # Customize arrow color if needed
                    ))

    # Traces for y2 columns (similar logic)
    if axes_data['y2']:
        for idx, y2_col in enumerate(columns_to_plot):
            if y2_col not in axes_data["y2"]:
                print(f'Skipping y2 column: {y2_col} (not in columns to plot)')
                continue

            if auto_title == True:
                y2_lineto_show = y2_col if axes_titles["y2"] == None else axes_titles["y2"]
            elif auto_title == False:
                y2_lineto_show = axes_titles["y2"]
            
            # Determine color based on sorted order for y2
            sorted_index = columns_to_plot.index(y2_col)
            line_color = colors[(sorted_index + len(axes_data["y1"])) % len(colors)]
            print(f'Processing y2 column: {y2_col} with color: {line_color}')
            
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
        print(f'ticksy: {ticksy}')
        if remove_zero:
            ticksy = [tick for tick in ticksy if tick != 0]
        
        formatted_ticks = [
            f"{tickprefix['y1'] if tickprefix['y1'] else ''}{clean_values(tick, decimal_places=0, decimals=False)}{ticksuffix['y1'] if ticksuffix['y1'] else ''}"
            for tick in ticksy
        ]
        print(f'formatted_ticks: {formatted_ticks}')
    else:
        ticksy = None


    if pd.api.types.is_datetime64_any_dtype(df.index):
        print(f'index is dt: {df.index}')
        x_start = df.index.min().timestamp()
        x_end = df.index.max().timestamp()
        x_ticks_numeric = np.linspace(x_start, x_end, num=5)
        x_ticks = [pd.to_datetime(tick, unit='s').strftime('%Y-%m-%d') for tick in x_ticks_numeric]
    else:
        x_ticks = None

    print(f'x_ticks: {x_ticks}')

    fig.update_layout(
        barmode=barmode,
        legend=dict(
            orientation=legend_orientation,
            yanchor="top",
            y=legend_placement['y'],
            xanchor="left",
            x=legend_placement['x'],
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor='rgba(0,0,0,0)',
            traceorder=traceorder
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
            tickformat=tickformat.get("y1", "")
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
                 bgcolor='rgba(0,0,0,0)', legend_orientation='v', dtick=None, tick0=None,
                 traceorder='normal', line_color='#2E2E2E', legend_placement=dict(x=0.01, y=1.1),
                 bar_color=None, fill=None, margin=dict(l=0, r=0, t=0, b=0), legend_font_size=16, decimals=True, decimal_places=1,
                 xtitle=None, barmode='stack', axes_title=dict(y1=None, y2=None), dimensions=dict(width=730, height=400), auto_title=True,
                 tickformat=dict(x=None, y1=".2s", y2=".2s"),font_family=None,font_color='black',file_type='svg',directory='../img',custom_annotation=[],buffer=None,
                 ytick_num=6,axes_font_colors=dict(y1='black',y2='black'),show_legend=True):
    
    if bgcolor == 'default':
        bgcolor = 'rgba(0,0,0,0)'
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Define a small buffer for x-axis range extension (e.g., 1 day on each side)
    if buffer != None:

        x_buffer = pd.Timedelta(days=buffer)
        x_range_start = df.index.min() - x_buffer
        x_range_end = df.index.max() + x_buffer
    
    else:
        x_range_start = df.index.min() 
        x_range_end = df.index.max() 

    print(f'axes_font_colors param: {axes_font_colors}')

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

    print(f'axes titles: {axes_title}')
    
    color_iter = iter(colors)  # Create an iterator for the colors
    rev_color_iter = reversed(colors[:-1])
    print(f'reversed color iter: {rev_color_iter}')
    for i, col in enumerate(line_col):
        color = line_color if i == 0 else next(rev_color_iter, "black")
        print(f'color for line{color}')
        print(f'line col: {df[col]}')
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            name=f'{col} ({tickprefix["y2"] if tickprefix["y2"] else ""}{clean_values(df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places)}{ticksuffix["y2"] if ticksuffix["y2"] else ""})',
            mode=mode,
            stackgroup=None if area == False else 'one',
            marker=dict(color=color),
            showlegend=show_legend
        ), secondary_y=y2_axis)

    if fill == None:
        # Add bar traces without specifying `width` to maintain default spacing
        for col in bar_col:
            color = next(filtered_iter, colors[1])  # Get the next color, fallback to first color if exhausted
            print(f'color for bar{color}')
            fig.add_trace(go.Bar(
                x=df.index,
                y=df[col],
                name=f'{col} ({tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places)}{ticksuffix["y1"] if ticksuffix["y1"] else ""})',
                marker=dict(color=color if bar_color == None else bar_color),
                showlegend=show_legend
            ), secondary_y=False)
    else:
        for col in bar_col:
            color = next(color_iter, colors[1])  # Get the next color, fallback to first color if exhausted
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                name=f'{col} ({tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places)}{ticksuffix["y1"] if ticksuffix["y1"] else ""})',
                marker=dict(color=color if bar_color == None else bar_color),
                fill=fill,  # This creates the area chart by filling to the x-axis (y=0)
                showlegend=show_legend
            ), secondary_y=False)

    if custom_annotation:
        for date in custom_annotation:
            if date in df.index:
                y_value = df.loc[date, bar_col[0]]
                annotation_text = f'{date}: {tickprefix["y1"] if tickprefix["y1"] else ""}{clean_values(y_value, decimal_places=decimal_places, decimals=decimals)}{ticksuffix["y1"] if ticksuffix["y1"] else ""}'

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
                    font=dict(size=16, family=font_family, color=font_color),
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
    x_start = df.index.min().timestamp()
    x_end = df.index.max().timestamp()
    x_ticks_numeric = np.linspace(x_start, x_end, num=5)
    x_ticks = [pd.to_datetime(tick, unit='s').strftime('%Y-%m-%d') for tick in x_ticks_numeric]

    fig.update_layout(
        barmode=barmode,
        autosize=True,
        legend=dict(
            orientation=legend_orientation,
            yanchor="top",
            y=legend_placement['y'],
            xanchor="left",
            x=legend_placement['x'],
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor='rgba(0,0,0,0)',
            traceorder=traceorder
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

    print(f'axes_title["y1"]: {axes_title["y1"]}')
    print(f'axes_font_colors["y1"]: {axes_font_colors["y1"]}')
    
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

def sorted_multi_line(df, title, save=False, colors=combined_colors, mode='lines', col=None, sort_col=None,
                      sort_list=True, area=False, tickprefix=None, ticksuffix=None, font_size=18,
                      bgcolor='rgba(0,0,0,0)', legend_orientation='h', tickangle=None,
                      traceorder='normal', legend_placement=dict(x=0.01, y=1.1), margin=dict(l=0, r=0, t=0, b=0),
                      legend_font_size=14, tickformat=dict(x="%b %y", y1=".2s", y2=".2s"), dtick=None, decimals=True, decimal_places=1,
                      dimensions=dict(width=730, height=400), remove_zero=False, custom_ticks=False,
                      connectgaps=True, descending=True, show_legend=True, tick0=None,font_family=None,font_color='black',file_type='svg'
                      ,directory='../img',custom_annotation=[],cumulative_sort=False,line_width=4,marker_size=10):
    
    combined_colors = colors

    print(f'tick0: {tick0}')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    traces = []

    x_buffer = pd.Timedelta(days=15)
    x_range_start = df.index.min() 
    x_range_end = df.index.max() 

    if sort_list:
        sort_list = rank_by_col(df=df, sort_col=sort_col, num_col=col, descending=descending,cumulative_sort=cumulative_sort)
    else:
        sort_list = df.columns.to_list()

    for idx, i in enumerate(sort_list):
        i_df = df[df[sort_col] == i]
        color = combined_colors[idx % len(combined_colors)] if descending else combined_colors[len(sort_list) - idx - 1]

        traces.append(go.Scatter(
            x=i_df.index,
            y=i_df[col],
            name=f'{i} ({tickprefix if tickprefix else ""}{clean_values(i_df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places) if i_df.index.max() == df.index.max() else 0}{ticksuffix if ticksuffix else ""})',
            line=dict(color=color, width=line_width),
            marker=dict(color=color, size=marker_size), 
            mode=mode,
            connectgaps=connectgaps,
            stackgroup=None if not area else 'one',
            showlegend=show_legend
        ))

        print(f'idx: {idx}')
        print(f'custom_annotation: {custom_annotation}')

        if idx == 0:
            if custom_annotation:
                for date in custom_annotation:
                    print(f'i_df index: {i_df}')
                    print(f'custom_annotation: {date}')
                    if date in i_df.index:
                        y_value = i_df.loc[date, col]
                        print(f'y_value: {y_value}')
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

    # # Calculate custom tick values for the y-axis if custom_ticks is True
    # if custom_ticks:
    #     figy = df[col]
    #     ticksy = list(np.linspace(min(figy), max(figy), num=5, endpoint=True))

    #     # Exclude zero if remove_zero is True, but keep the spacing
    #     if remove_zero:
    #         ticksy = [tick for tick in ticksy if tick != 0]
    # else:
    #     ticksy = None  # Default to None if not using custom ticks

    # Continue with x-axis ticks as before
    x_start = df.index.min().timestamp()
    x_end = df.index.max().timestamp()
    x_ticks_numeric = np.linspace(x_start, x_end, num=5)
    x_ticks = [pd.to_datetime(tick, unit='s').strftime('%Y-%m-%d') for tick in x_ticks_numeric]  # Adjust to day

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
            yanchor="top",
            y=legend_placement['y'],
            xanchor="left",
            x=legend_placement['x'],
            font=dict(size=legend_font_size, family=font_family, color=font_color),
            bgcolor='rgba(0,0,0,0)',
            traceorder=traceorder
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=15),
        font=dict(size=font_size, family=font_family, color=font_color),
        width=dimensions['width'],
        height=dimensions['height'],
        margin=margin
    )
    
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
                     use_single_color=False):

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
            name = f'{i} ({tickprefix if tickprefix else ""}{clean_values(df[df[sort_col] == i][col].iloc[-1], decimal_places=decimal_places, decimals=decimals)}{ticksuffix if ticksuffix else ""})' 
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

    if orientation == 'v':
        if not showlegend:
            ytickprefix = None
            yticksuffix = None
            tickvals = list(range(index_length))  # Generate tick values for the y-axis
            ticktext = [""] * index_length  # Empty strings for tick labels on the y-axis
            xtickprefix = None  # No prefix for x-axis if legend is not shown
            xticksuffix = None  # No suffix for x-axis if legend is not shown
        else:
            ytickprefix = tickprefix
            yticksuffix = ticksuffix
            tickvals = list(range(index_length))  # Tick values based on index length for y-axis
            ticktext = [""] * index_length  # No specific ticktext if showing legend
            xtickprefix = None  # Adjust if needed based on your requirements
            xticksuffix = None  # Adjust if needed based on your requirements
    else:  # Horizontal orientation
        if not showlegend:
            print(f'no legend, horizontal')
            ytickprefix = None
            yticksuffix = None
            tickvals = None  # No specific tick values for y-axis
            ticktext = [""] * index_length  # Empty strings for tick labels on the y-axis
            xtickprefix = tickprefix  # Use tickprefix for x-axis if not showing legend
            xticksuffix = ticksuffix  # Use ticksuffix for x-axis if not showing legend
        else:
            print(f'legend, horizontal')
            ytickprefix = None
            yticksuffix = None
            tickvals = list(range(index_length))  # No specific tick values for y-axis
            ticktext = [""] * index_length  # No specific ticktext if showing legend
            xtickprefix = tickprefix  # Use tickprefix for x-axis if showing legend
            xticksuffix = ticksuffix  # Use ticksuffix for x-axis if showing legend

    print(f'ytickvals: {tickvals}')
    print(f'yticktext: {ticktext}')
    print(f'ytickprefix: {ytickprefix}')
    print(f'xtickprefix: {xtickprefix}')

    fig.update_layout(
        xaxis_title=dict(
            font=dict(size=font_size, family=font_family, color=font_color),
        ),
        xaxis=dict(tickangle=tickangle,
                   tickfont=dict(size=font_size, family=font_family, color=font_color),
                   tickprefix=xtickprefix,
                   ticksuffix=xticksuffix,
                   tickformat=tickformat
                   ),

        yaxis=dict(tickprefix=ytickprefix,
                   ticksuffix=yticksuffix,
                   tickangle=tickangle,
                   tickfont=dict(size=font_size, family=font_family, color=font_color),
                   tickvals=tickvals,  # Set tick values to blank if not showing legend
                   ticktext=ticktext),
                   

    )

    # Figure
    if save:
        pio.write_image(fig, f'{directory}/{title}.{file_type}', engine="kaleido")

    return fig

def sorted_bar_chart(df, title, save=False, colors=combined_colors, col=None, sort_col=None, sort_list=True,
                      tickprefix=None, ticksuffix=None, font_size=18, remove_zero=False, custom_ticks=False,
                      bgcolor='rgba(0,0,0,0)', legend_orientation='h', bar_orientation='v', tickangle=None,
                      dtick=None, margin=dict(l=0, r=0, t=0, b=0), decimals=True, traceorder='normal',
                      tickformat=None, legend_placement=dict(x=0.01, y=1.1), legend_font_size=16, decimal_places=1,
                      barmode='stack', dimensions=dict(width=730, height=400), descending=True,show_legend=True,tick0=None,font_family=None,font_color='black',
                      file_type='svg',directory='../img',custom_annotation=[],buffer=None,ytick_num=6,
                      cumulative_sort=False):
    print(f'cumulative_sort: {cumulative_sort}')
    
    print(f'sorted_bar_legend_orientation: {legend_orientation}')

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    combined_colors = colors

    if buffer != None:

        x_buffer = pd.Timedelta(days=buffer)
        x_range_start = df.index.min() - x_buffer
        x_range_end = df.index.max() + x_buffer
    
    else:
        x_range_start = df.index.min() 
        x_range_end = df.index.max() 

    print(f'x_range_start:{x_range_start}')

    traces = []

    if sort_list:
        sort_list = rank_by_col(df=df, sort_col=sort_col, num_col=col, descending=descending, cumulative_sort=cumulative_sort)
    else:
        sort_list = df.columns.to_list()

    print(f'df columns: {df.columns}')

    # Iterate over sorted columns and assign colors accordingly
    for idx, i in enumerate(sort_list):
        i_df = df[df[sort_col] == i]

        # Determine the color based on descending order
        if descending:
            column_color = combined_colors[idx % len(combined_colors)]  # Normal order for descending
        else:
            column_color = combined_colors[len(sort_list) - idx - 1]  # Reverse order for ascending

        print(f'i_df:{i_df}')
        print(f'col:{col}')
        traces.append(go.Bar(
            x=i_df.index if bar_orientation == 'v' else i_df[col],
            y=i_df[col] if bar_orientation == 'v' else i_df.index,
            orientation=bar_orientation,
            showlegend=show_legend,
            name=f'{i} ({tickprefix if tickprefix else ""}{clean_values(i_df[col].iloc[-1], decimals=decimals, decimal_places=decimal_places) if i_df.index.max() == df.index.max() else 0}{ticksuffix if ticksuffix else ""})',
            marker=dict(color=column_color)
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
    x_start = df.index.min().timestamp()
    x_end = df.index.max().timestamp()
    x_ticks_numeric = np.linspace(x_start, x_end, num=5)
    x_ticks = [pd.to_datetime(tick, unit='s').strftime('%Y-%m-%d')  for tick in x_ticks_numeric]  # Convert back to datetime

    print(f'x_ticks:{x_ticks}')

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
            bgcolor='rgba(0,0,0,0)',
            traceorder=traceorder
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        uniformtext=dict(mode="show", minsize=15),  # Adjust minsize as needed
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
              show_legend=False,text_font_size=12,text_font_color='white',texttemplate=None):
    
    original_labels = df[index_col].unique()
    print(f'original_labels: {original_labels}')

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
    print(f'{textinfo}, {labels}')

    print(f'textinfo: {textinfo}')

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
        annotations=[dict(
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
        )],
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
    
