import plotly.io as pio

import sys
# sys.path.append('E:\Projects\ournetwork\chart_builder\scripts')  
import os
current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the pipeline scripts directory to sys.path
# sys.path.append(os.path.join(current_dir, 'chart_builder', 'scripts'))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# print("sys.path:", sys.path)
# print("Current working directory:", os.getcwd())
# print("Current directory:", current_dir)
# Now you can import data_pipeline
# from pipeline import data_pipeline  # Adjust the import based on your actual module structure

from chart_builder.scripts.utils import colors, clean_values, clean_values_dollars, ranked_cleaning, to_percentage, rank_by_col, rank_by_columns, normalize_to_percent, data_processing, top_other_ts_by_col, top_other_ts_by_columns, top_ts_by_col, top_ts_only_by_columns, cleaning, cleaning_values, top_by_col, top_other_by_col,to_time
from chart_builder.scripts.plots import simple_bar_plot, simple_line_plot, sorted_bar_chart, sorted_multi_line, ranked_bar_chart, line_and_bar, pie_chart, datetime_format

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import plotly.offline as pyo
import plotly.colors as pc

import pandas as pd
import svgwrite
import base64
from io import BytesIO

combined_colors = colors()
font_family = "IBM Plex Mono"

class visualization_pipeline():
    def __init__(self,chart_type, title, file=None, df=None,cols_to_plot='All', is_file_path=False, watermark=None,dimensions=dict(height=351, width=730), 
                 subtitle=None, colors=combined_colors, axes_data=dict(y1=[],y2=[]), axes_titles=dict(y1=None,y2=None),line_factor=1.5,
                  mode='lines',area=False, fill=None,tickprefix=dict(y1=None,y2=None), ticksuffix=dict(y1=None,y2=None),user_sort_list=None, user_color_map=None,
                  annotation_prefix=None,annotation_suffix=None, legend_orientation='v',show_legend=False, annotations=False, 
                  max_annotation=False,bgcolor='rgba(0,0,0,0)', tickangle=None, legend_placement=dict(x=0.2,y=0.9),ytickvals=None, yticktext=None,
                  margin=dict(l=0, r=0, t=50, b=0), sort_list = True,tick0='min', remove_zero=False, custom_ticks=False,
                  line_width=4, marker_size=10,marker_col=None,cumulative_sort=True,decimal_places=1,decimals=True,groupby=None, 
                itemsizing='constant',num_col=None,barmode='stack',tickformat=dict(x='%b %d <br>%y',y1=None,y2=None),y_log=False,
                textposition="outside",orientation="v",dtick=None,traceorder='normal',line_color=None,hole_size=0,
                time_frame='All', resample_freq=None,legend_font_size=12,font_size=16,annotation_font_size=25,turn_to_time=True,time_col=None,
                fillna=False,keepna=False,dropna_col=False, topn=4, capwords=None,logo=None,bar_col=None, line_col=None,
                y2_col=None,y2=False,text=False,text_font_size=14,text_freq=1,dropna=False,index_col=None, to_reverse=False,
                to_percent=False,normalize=False,start_date=None, end_date=None,connectgaps=True,drop_duplicates=True,auto_title=False,descending=True,
                set_time_col=False,drop_mid_timefreq=True,agg_func='sum',clean_dates=True,ffill=False,font_family=font_family,font_color='black',
                directory='../img',custom_annotation=None,buffer=None,textinfo='percent+label',ytick_num=6,discrete=False,save_directory='../img/',
                axes_font_colors=dict(y1='black',y2='black'),file_type='svg',texttemplate='%{label}<br>%{percent}',use_single_color=False,
                days_first=False,autosize=True,delimiter=',',min_tick_spacing=125,legend_background=dict(bgcolor='white',bordercolor='black',
                                                                                                    borderwidth=1, itemsizing='constant',
                                                                                                    yanchor="top",xanchor="center",buffer=5)
    ):
        """
        Chart Visualization Pipeline

        Args:
            chart_type (str): The type of chart to render (e.g., 'bar', 'line').
            title (str): The title of the chart.
            file (str, optional): Path to the data file. Defaults to None.
            df (pd.DataFrame, optional): DataFrame containing the data to plot. Defaults to None.
            cols_to_plot (list, optional): List of columns to plot. Defaults to `All`.
            is_file_path (bool, optional): Flag indicating if the file parameter is a file path. Defaults to False.
            watermark (str, optional): Path to the watermark image. Defaults to None.
            dimensions (dict, optional): Dimensions of the chart. Defaults to {'height': 351, 'width': 730}.
            subtitle (str, optional): Subtitle of the chart. Defaults to None.
            colors (list, optional): List of colors to use for the chart. Defaults to combined_colors.
            axes_data (dict, optional): Data for the chart axes. Defaults to {'y1': [], 'y2': []}.
            axes_titles (dict, optional): Titles for the chart axes. Defaults to {'y1': None, 'y2': None}.
            line_factor (float, optional): Factor to adjust dashed-line height. Defaults to 1.5.
            mode (str, optional): Mode for line charts. Defaults to 'lines'. Expects Plotly options.
            area (bool, optional): Flag indicating if the chart is an area chart. Defaults to False.
            fill (str, optional): Fill style for the chart. Defaults to 'none'. Expects Plotly options.
            tickprefix (dict, optional): Tick prefix for the chart axes. Defaults to {'y1': None, 'y2': None}.
            ticksuffix (dict, optional): Tick suffix for the chart axes. Defaults to {'y1': None, 'y2': None}.
            annotation_prefix (str, optional): Prefix for pie chart annotations. Defaults to None.
            annotation_suffix (str, optional): Suffix for pie chart annotations. Defaults to None.
            legend_orientation (str, optional): Orientation of the legend. Defaults to 'v'. Expects Plotly options.
            show_legend (bool, optional): Flag indicating if the legend should be shown. Defaults to False.
            annotations (bool, optional): Flag indicating if annotations should be shown for line, bar, and pie charts. Defaults to False.
            max_annotation (bool, optional): Flag indicating if only the maximum value should be annotated. Defaults to False.
            tickangle (int, optional): Angle of the ticks. Defaults to None. Expects Plotly options.
            legend_placement (dict, optional): Placement of the legend. Defaults to {'x': 0.2, 'y': 0.9}.
            margin (dict, optional): Margin for the chart. Defaults to {'l': 0, 'r': 0, 't': 50, 'b': 0}.
            sort_list (bool, optional): Flag indicating if the charted data should be sorted. Defaults to False.
            line_width (float, optional): Width of the lines in the chart. Defaults to 4.
            marker_size (float, optional): Size of the markers in the chart. Defaults to 6.
            cumulative_sort (bool, optional): Flag indicating if the charted data should be cumulatively sorted. Defaults to False.
            decimals (bool, optional): Flag indicating if the charted data should be formatted to a fixed number of decimal places. Defaults to True.
            decimal_places (int, optional): Number of decimal places to format the charted data. Defaults to 1.
            groupby (str, optional): Column to group the data by. Defaults to None.
            num_col (str, optional): Column to use for the number values. Defaults to None.
            barmode (str, optional): Bar mode for the chart. Defaults to 'stack'. Expects Plotly options.
            tickformat (dict, optional): Tick format for the chart axes. Defaults to {'x' :'%b %d <br>%y', 'y1': None, 'y2': None}.
            y_log (bool, optional): Flag indicating if the y-axis should be logarithmic. Defaults to False.
            textposition (str, optional): Position of the text annotations. Defaults to 'outside'. Expects Plotly options.
            orientation (str, optional): Orientation of the chart. Defaults to 'v'. Only applicable for ranked bar charts. Expects Plotly options. 
            line_color (str, optional): Color of the line for a line_and_bar chart.  If None, defaults to colors passed in init.
            hole_size (float, optional): Size of the hole for a donut chart. Defaults to 0.
            legend_font_size (int, optional): Font size for the legend. Defaults to 12.
            font_size (int, optional): Font size for the chart. Defaults to 16.
            annotation_font_size (int, optional): Font size for the pie chart annotations. Defaults to 25.
            turn_to_time (bool, optional): Flag indicating if the x-axis should be converted to a time series. Defaults to True.
            bar_col (str, optional): Column to use for the bar chart values in a line_and_bar chart. Defaults to None.
            line_col (str, optional): Column to use for the line chart values in a line_and_bar chart. Defaults to None.
            y2 (bool, optional): Flag indicating if the y2 axis should be used in a line_and_bar chart. Defaults to False.
            text (bool, optional): Flag indicating if text annotations should be shown. Applicable for bar and line_and_bar charts. Defaults to False.
            text_font_size (int, optional): Font size for the text annotations. Defaults to 14.
            text_freq (int, optional): Frequency of the text annotations. Defaults to 1.
            to_reverse (bool, optional): Flag indicating if the chart should be reversed. Applicable for ranked bar charts. Defaults to False.
            to_percent (bool, optional): Flag indicating if the chart should display values as percentages. Defaults to False.
            normalize (bool, optional): Flag indicating if the chart should normalize values to percent. Defaults to False.
            auto_title (bool, optional): Flag indicating if the chart title should be automatically generated. Defaults to False.
            font_color (str, optional): Default font color for the chart. Defaults to 'black'.
            save_directory (str, optional): Directory to save the chart. Defaults to './img'.
            buffer (float, optional): Buffer size for the x-axis of the chart. Applicable for datetime axes. Defaults to None.
            textinfo (str, optional): Text information to display on the chart. Defaults to 'percent+label' Applicable for pie charts. Expects Plotly options.
            texttemplate (str, optional): Template for the text annotations. Defaults to '%{label}<br>%{percent}'. Applicable for pie charts. Expects Plotly options.
            axes_font_colors (dict, optional): Font colors for the chart axes. Defaults to {'y1': 'black', 'y2': 'black'}.
            file_type (str, optional): File type for the chart export. Defaults to 'svg'.
            use_single_color (bool, optional): Flag indicating if a single color should be used for all chart elements. Defaults to False. Applicable for ranked bar charts.
            min_tick_spacing (float, optional): Minimum tick spacing for the chart. Defaults to 150.
            bgcolor (str, optional): Background color for the chart. Defaults to 'rgba(0,0,0,0)'. Expects Plotly options.
            legend_background (dict, optional): Background styling for the legend. Defaults to dict(bgcolor='white', bordercolor='black',
                                                                                                    borderwidth=1, itemsizing='constant',
                                                                                                    yanchor="top",xanchor="center",buffer=5).
            """
        
        custom_template = pio.templates["plotly"]
        custom_template.layout.font.family = font_family

        # Set the custom template as the default
        pio.templates["custom"] = custom_template
        pio.templates.default = "custom"
        
        if is_file_path == True:
            func_file = file
        else:
            file_path = f'../data/{file}'
            func_file = file_path

        if watermark != None:
            watermark_path = f'../img/Logos/{watermark}'
        else:
            watermark_path = None
        logo_path = f'../img/Logos/{logo}'

        if chart_type != 'line and bar':
            
           # Check if y2 data is provided in axes_data
            if axes_data and axes_data.get('y2') and isinstance(axes_data['y2'], list) and len(axes_data['y2']) > 0:
                y2 = True
            else:
                y2 = False  # Ensure y2 is False if no data is provided

            # If only y1 data is passed, handle it
            if cols_to_plot is None and axes_data:
                # print(f'Adding axes_data from y1')
                cols_to_plot = axes_data.get('y1', [])  # Default to y1 axis data if available
                if y2:  # Add y2 data if it's available
                    cols_to_plot += axes_data['y2']

            if not axes_data or (axes_data['y1'] == [] and axes_data['y2'] == []):
                axes_data = {
                    'y1': cols_to_plot if cols_to_plot else [],  # Use cols_to_plot if available
                    'y2': []  # Keep y2 as empty unless specified
                }
            # print(f'Initialized axes_data: {axes_data}')

            # Proceed with the rest of your logic for plotting...

        if chart_type == 'line and bar' and cols_to_plot == None:
            cols_to_plot = bar_col + line_col
        elif groupby and num_col:
            cols_to_plot =[groupby,num_col]
        elif cols_to_plot == None:
            raise('Error: Please Add to cols_to_plot')

        # if index_col == None:
        #     turn_to_time = False

        if chart_type == 'ranked bar' or chart_type == 'pie':
            turn_to_time=False

        if df is None:
            df = data_processing(path=func_file,file=None,cols=cols_to_plot,turn_to_time=turn_to_time,time_col=time_col,
                             fillna=fillna,keepna=keepna,dropna_col=dropna_col,dropna=dropna,start_date=start_date,end_date=end_date,drop_duplicates=drop_duplicates,
                             resample_freq=resample_freq,set_time_col=set_time_col,drop_mid_timefreq=drop_mid_timefreq,agg_func=agg_func,
                             to_clean_dates=clean_dates,sort_col=groupby,dayfirst=days_first,delimiter=delimiter)
        else:
            df=df.copy()

        if tick0 == 'min' and turn_to_time==True:
            tick0 = df.index.min()
        else:
            tick0=None

        # print(f'tick0: {tick0}')
        # print(f'turn_to_time: {turn_to_time}')
        
        if cols_to_plot == 'All':
            cols_to_plot = df.columns  # Select all columns
            if y2 == False:
                axes_data['y1'] = cols_to_plot

        if normalize == True:
            # # print(f'normalizing...')
            df = normalize_to_percent(df=df,num_col=num_col)
            # print(f'df: {df}')
               
        cols_to_plot = list(set(cols_to_plot))

        if to_percent == True:
            if groupby == None:
                df[cols_to_plot] = df[cols_to_plot] * 100
            else:
                df[num_col] = df[num_col]*100

        if descending == False:
            traceorder = 'reversed'
        
        # axes_data['y1'] = cols_to_plot if axes_data.any() # if no specific axis we default plotting cols to y1

        # Ensure cols_to_plot is a list and not a tuple
        if isinstance(cols_to_plot, str):
            cols_to_plot = [cols_to_plot]  # Convert single string to list

        if marker_col is not None:
            if isinstance(marker_col, str):
                marker_col = [marker_col]  # Convert single string to list
            selected_columns = list(cols_to_plot) + list(marker_col)
        else:
            selected_columns = list(cols_to_plot)

        # Check which columns exist before selection
        existing_columns = [col for col in selected_columns if col in df.columns]

        if not existing_columns:
            raise KeyError(f"None of the requested columns {selected_columns} exist in the DataFrame.")

        df = df[existing_columns]

        # df = df[[cols_to_plot + [marker_col]]] if marker_col is not None else df[cols_to_plot]
        self.df = df.copy()
        self.user_sort_list = user_sort_list
        self.user_color_map = user_color_map
        self.y_log = y_log
        self.marker_col = marker_col
        self.discrete = discrete
        self.line_factor = line_factor
        self.save_directory = os.path.abspath(save_directory)
        self.autosize = autosize
        self.legend_background = legend_background
        self.use_single_color=use_single_color
        self.cumulative_sort = cumulative_sort
        self.min_tick_spacing = min_tick_spacing
        self.texttemplate = texttemplate
        self.file_type = file_type
        self.font_size = font_size
        self.marker_size = marker_size
        self.axes_font_colors = axes_font_colors
        self.ytick_num = ytick_num
        self.directory = directory
        self.custom_annotation = custom_annotation
        self.font_color = font_color
        self.font_family = font_family
        self.remove_zero = remove_zero
        self.custom_ticks=custom_ticks
        self.cols_to_plot = cols_to_plot
        self.title = title
        self.subtitle = subtitle
        self.area = area
        self.ytickvals=ytickvals, 
        self.yticktext=yticktext,
        self.annotations = annotations
        self.show_legend = show_legend
        self.groupby = groupby
        self.num_col = num_col
        self.legend_orientation=legend_orientation
        self.legend_placement = legend_placement
        self.margin = margin
        self.dtick = dtick
        self.decimal_places = decimal_places
        self.decimals = decimals
        self.tickangle = tickangle
        self.descending=descending
        self.tickformat = tickformat
        self.tick_prefix=tickprefix
        self.ticksuffix = ticksuffix
        self.traceorder = traceorder
        self.barmode = barmode
        self.mode = mode
        self.colors = colors
        self.fill = fill
        self.topn = topn
        self.textinfo = textinfo
        self.chart_type = chart_type
        self.bgcolor = bgcolor
        self.fig = None
        self.datetime_tick = turn_to_time
        self.tick0 = tick0
        self.title_position = None
        self.watermark = watermark_path
        self.logo = logo_path
        self.legend_font_size = legend_font_size
        self.date_position = None
        self.axes_data = axes_data
        self.bar_col = bar_col
        self.line_col = line_col
        self.line_color = line_color
        self.axes_titles = axes_titles
        self.y2 = y2
        self.text = text
        self.text_freq = text_freq
        self.text_font_size = text_font_size
        self.dimensions = dimensions
        self.textposition = textposition
        self.plot_orientation = orientation
        self.to_reverse = to_reverse
        self.turn_to_time = turn_to_time
        self.connectgaps = connectgaps
        self.auto_title = auto_title
        self.max_annotation = max_annotation
        self.hole_size = hole_size
        self.line_width = line_width
        self.annotation_font_size=annotation_font_size
        self.submissions_data = None
        self.current_submission_index = 0
        self.annotation_prefix = annotation_prefix
        self.annotation_suffix = annotation_suffix
        self.sort_list = sort_list
        self.buffer = buffer

    def create_fig(self):
        # print(f'logo path: {self.logo}')
        if self.chart_type == 'line':
            self.line_plot()
        elif self.chart_type == 'bar':
            self.bar_plot()
        elif self.chart_type == 'line and bar':
            self.line_and_bar_plot()
        elif self.chart_type == 'pie':
            self.turn_to_time = False
            self.pie_plot()
        elif self.chart_type == 'ranked bar':
            self.turn_to_time = False
            # self.group_data()
            self.ranked_bar_plot()

    def return_df(self):
        return self.df.copy()
    
    def show_fig(self,browser=False):
        if browser==False:
            pyo.iplot(self.fig)
        else:
            pyo.plot(self.fig, filename=f'{self.title}.html',auto_open=True)
    
    def clean_columns(self, capwords=None, clean_words=None):
        # Extract y1 and y2 lists from axes_data
        y1_list = self.axes_data.get('y1', [])
        y2_list = self.axes_data.get('y2', [])

        # Clean the DataFrame and axis data
        self.df, self.cols_to_plot, self.bar_col, self.line_col, self.y1_list, self.y2_list, self.groupby, self.num_col = cleaning(
            df=self.df,
            cols_to_plot=self.cols_to_plot, 
            bar_col=self.bar_col,
            line_col=self.line_col,
            groupby=self.groupby,
            num_col=self.num_col,
            y1_list=y1_list,  # Pass y1 list
            y2_list=y2_list,       # Pass y2 list
            capwords=capwords, 
            clean_words=clean_words
        )

        # Update the axes_data with the cleaned values
        self.axes_data['y1'] = self.y1_list  # Set cleaned y1 values
        self.axes_data['y2'] = self.y2_list  # Set cleaned y2 values

        self.cols_to_plot = list(set(self.cols_to_plot))

    def clean_values(self):
        self.df = cleaning_values(df=self.df)

    def show_index_and_cols(self):
        return print(f'Columns: {self.df.columns} \nIndex: {self.df.index}')
    
    def keep_top_n(self, topn=None, other=True):
        # print(f'topn: {topn}')
        # print(f'other: {other}')
        if topn != None:
            self.topn = topn
        if self.turn_to_time == False:
            if other == False:
                if self.groupby != None:
                    self.df = top_by_col(df=self.df, sort_col=self.groupby, sum_col=self.num_col, num=self.topn,latest=not self.cumulative_sort)
            else:
                if self.groupby != None:
                    self.df = top_other_by_col(df=self.df, sort_col=self.groupby, sum_col=self.num_col, num=self.topn,latest=not self.cumulative_sort)
                    # Append only if y1 is a list
                    if isinstance(self.axes_data['y1'], list):
                        self.axes_data['y1'].append('other')
        else:
            if other == True:
                if self.groupby == None:
                    self.df = top_other_ts_by_columns(df=self.df, topn=self.topn)
                else:
                    self.df = top_other_ts_by_col(df=self.df, num_col=self.num_col, sort_col=self.groupby, topn=self.topn)

                # Convert to list if it's an Index type, then append 'Other'
                if isinstance(self.axes_data['y1'], pd.Index):
                    self.axes_data['y1'] = self.axes_data['y1'].tolist()

                # Append only if y1 is a list
                if isinstance(self.axes_data['y1'], list):
                    self.axes_data['y1'].append('other')
                    
                # print(f'self.axes_data: {self.axes_data["y1"]}')

                self.cols_to_plot.append('other')

                # print(f'self.cols_to_plot: {self.cols_to_plot}')
                
            else:
                if self.groupby == None:
                    self.df = top_ts_only_by_columns(df=self.df, topn=self.topn)
                else:
                    self.df = top_ts_by_col(df=self.df, num_col=self.num_col, sort_col=self.groupby, topn=self.topn)
            

        # print(f'df after: {self.df}')

    def line_plot(self):
        print("Generating line plot...")
        # print(f'axes titles at viz pipeline: {self.axes_titles}')
        if self.groupby == None:
            # print(f'No GroupBy Col')
            # print(f'cols to plot: {self.cols_to_plot}')
            # print(f'axes data to plot: {self.axes_data}')
            
            y1_columns = self.axes_data['y1']
            y2_columns = self.axes_data['y2']

            # Exclude y2 columns from y1
            filtered_y1 = [col for col in y1_columns if col not in y2_columns]

            fig = simple_line_plot(df=self.df, title=self.title, annotations=self.annotations, show_legend=self.show_legend,
                                area=self.area, legend_orientation=self.legend_orientation,
                                legend_placement=self.legend_placement, margin=self.margin,ytickvals=self.ytickvals,yticktext=self.yticktext,
                                dtick=self.dtick, mode=self.mode, tickprefix=self.tick_prefix,min_tick_spacing=self.min_tick_spacing,
                                ticksuffix=self.ticksuffix, tickformat=self.tickformat,bgcolor=self.bgcolor,legend_font_size=self.legend_font_size,
                                axes_titles=self.axes_titles,dimensions=self.dimensions,axes_data={'y1': filtered_y1, 'y2': y2_columns},
                                fill=self.fill,connectgaps=self.connectgaps,max_annotation=self.max_annotation,descending=self.descending,traceorder=self.traceorder,
                                tickangle=self.tickangle,text=self.text,text_freq=self.text_freq,decimals=self.decimals,decimal_places=self.decimal_places,tick0=self.tick0,
                                remove_zero=self.remove_zero, custom_ticks=self.custom_ticks,font_family=self.font_family,font_color=self.font_color,directory=self.directory,colors=self.colors,
                                custom_annotation=self.custom_annotation,ytick_num=self.ytick_num,axes_font_colors=self.axes_font_colors,
                                auto_title=self.auto_title,file_type = self.file_type,buffer=self.buffer,cumulative_sort=self.cumulative_sort,marker_size=self.marker_size,line_width=self.line_width,
                                sort_list=self.sort_list,datetime_tick=self.datetime_tick,autosize=self.autosize,legend_background=self.legend_background, font_size=self.font_size)
            self.fig = fig
            return fig
        else:

            # print(f'GroupBy Col: {self.groupby}')
            fig = sorted_multi_line(df=self.df, title=self.title,col=self.num_col, sort_col=self.groupby,area=self.area,legend_orientation=self.legend_orientation,
                                    legend_placement=self.legend_placement,margin=self.margin,axes_titles=self.axes_titles,y_log=self.y_log,
                                    dtick=self.dtick,mode=self.mode, tickprefix=self.tick_prefix['y1'],min_tick_spacing=self.min_tick_spacing,user_color_map=self.user_color_map,user_sort_list=self.user_sort_list,
                                    ticksuffix=self.ticksuffix['y1'],tickformat=self.tickformat,bgcolor=self.bgcolor,legend_font_size=self.legend_font_size,dimensions=self.dimensions,
                                    connectgaps=self.connectgaps,descending=self.descending,traceorder=self.traceorder,tickangle=self.tickangle, show_legend=self.show_legend,tick0=self.tick0
                                    ,remove_zero=self.remove_zero, custom_ticks=self.custom_ticks,font_family=self.font_family,font_color=self.font_color,directory=self.directory,colors=self.colors
                                    ,custom_annotation=self.custom_annotation,decimal_places=self.decimal_places,decimals=self.decimals,file_type = self.file_type,cumulative_sort=self.cumulative_sort,
                                    marker_size=self.marker_size,line_width=self.line_width, font_size=self.font_size,legend_background=self.legend_background,marker_col = self.marker_col)
            self.fig = fig
            return fig

    def bar_plot(self):
        print("Generating bar plot...")
        if self.groupby == None:
            # print(f'No GroupBy Col')
            # print(f'auto_title: {self.auto_title}')
   
            fig = simple_bar_plot(df=self.df, title=self.title, annotations=self.annotations, show_legend=self.show_legend,
                                legend_orientation=self.legend_orientation,
                                legend_placement=self.legend_placement, margin=self.margin,
                                dtick=self.dtick, tickprefix=self.tick_prefix,barmode=self.barmode,axes_titles=self.axes_titles,
                                ticksuffix=self.ticksuffix, tickformat=self.tickformat,bgcolor=self.bgcolor,legend_font_size=self.legend_font_size,
                                text=self.text,text_freq=self.text_freq, text_font_size=self.text_font_size,dimensions=self.dimensions,max_annotation=self.max_annotation,
                                axes_data=self.axes_data,descending=self.descending,traceorder=self.traceorder,tickangle=self.tickangle,text_position=self.textposition,
                                decimals=self.decimals,colors=self.colors,tick0=self.tick0,remove_zero=self.remove_zero, custom_ticks=self.custom_ticks,font_family=self.font_family,
                                font_color=self.font_color,directory=self.directory,cumulative_sort=self.cumulative_sort,
                                custom_annotation=self.custom_annotation,buffer=self.buffer,decimal_places=self.decimal_places,ytick_num=self.ytick_num,min_tick_spacing=self.min_tick_spacing,
                                auto_title=self.auto_title,datetime_tick=self.datetime_tick,file_type = self.file_type,sort_list=self.sort_list, font_size=self.font_size,legend_background=self.legend_background)
            self.fig = fig
            return fig
        else:
            # print(f'GroupBy Col: {self.groupby}')
            # sorted_bar_chart(df, title, save=False, combined_colors=combined_colors, col=None, sort_col=None, sort_list=True,
            #         tickprefix=None, ticksuffix=None, font_size=18,
            #         bgcolor='rgba(0,0,0,0)', legend_orientation='h', bar_orientation='v', tickangle=None,
            #         dtick=None, margin=dict(l=0, r=0, t=0, b=0), decimals=True, traceorder='normal',
            #         tickformat=None,legend_placement=dict(x=0.01,y=1.1),legend_font_size=16,decimal_places=1,
            #         barmode='stack',dimensions=dict(width=730,height=400)):

            # print(f'legend_orientation: {self.legend_orientation}')

            fig = sorted_bar_chart(df=self.df, title=self.title,col=self.num_col, sort_col=self.groupby,legend_orientation=self.legend_orientation,
                                    legend_placement=self.legend_placement,margin=self.margin,min_tick_spacing=self.min_tick_spacing,
                                    dtick=self.dtick,barmode=self.barmode, tickprefix=self.tick_prefix['y1'],
                                    ticksuffix=self.ticksuffix['y1'],tickformat=self.tickformat,bgcolor=self.bgcolor,legend_font_size=self.legend_font_size,
                                    dimensions=self.dimensions,descending=self.descending,traceorder=self.traceorder,tickangle=self.tickangle,colors=self.colors,
                                     show_legend=self.show_legend,tick0=self.tick0,remove_zero=self.remove_zero, custom_ticks=self.custom_ticks,font_family=self.font_family,font_color=self.font_color,directory=self.directory,
                                custom_annotation=self.custom_annotation,decimal_places=self.decimal_places,decimals=self.decimals,buffer=self.buffer,ytick_num=self.ytick_num,
                                  file_type = self.file_type,cumulative_sort=self.cumulative_sort,text=self.text,text_freq=self.text_freq, text_position=self.textposition,text_font_size=self.text_font_size,autosize=self.autosize,legend_background=self.legend_background,font_size=self.font_size)
            self.fig = fig
            return fig
    
    def line_and_bar_plot(self):
        print("Generating line and bar plot...")

        # print(f'axes titles: {self.axes_titles}')

        fig = line_and_bar(df=self.df,title=self.title,y2_axis=self.y2,bar_col=self.bar_col,line_col=self.line_col,cumulative_sort=self.cumulative_sort,legend_orientation=self.legend_orientation,
                           axes_title=self.axes_titles, tickprefix=self.tick_prefix,ticksuffix=self.ticksuffix,dimensions=self.dimensions,text=self.text,text_freq=self.text_freq,
                           margin=self.margin,auto_title=self.auto_title,tickformat=self.tickformat,barmode=self.barmode,tickangle=self.tickangle, fill=self.fill,
                           area=self.area,colors = self.colors,tick0=self.tick0,dtick=self.dtick,remove_zero=self.remove_zero, custom_ticks=self.custom_ticks,font_family=self.font_family,font_color=self.font_color,directory=self.directory,min_tick_spacing=self.min_tick_spacing,
                           custom_annotation=self.custom_annotation,decimal_places=self.decimal_places,decimals=self.decimals,buffer=self.buffer,ytick_num=self.ytick_num,file_type = self.file_type,show_legend=self.show_legend,axes_font_colors=self.axes_font_colors,
                           legend_placement=self.legend_placement,line_color=self.line_color,bgcolor=self.bgcolor,autosize=self.autosize,legend_background=self.legend_background,legend_font_size=self.legend_font_size, font_size=self.font_size,mode=self.mode)
        self.fig = fig
        return fig
    
    def pie_plot(self):
        print('Generating pie chart...')
        # print(f'self.textinfo: {self.textinfo}')
        # def pie_chart(df, sum_col, index_col, title, save=False,colors=combined_colors,bgcolor='rgba(0,0,0,0)',annotation_prefix="$", annotation_font_size=25,
        #       decimals=True,legend_font_size=16,font_size=18, legend_placement=dict(x=0.01,y=1.1),margin=dict(l=0, r=0, t=0, b=0),hole_size=.6,line_width=0,
        #       legend_orientation='v',decimal_places=1,itemsizing='constant',dimensions=dict(width=730,height=400)):
        fig = pie_chart(df=self.df, sum_col=self.num_col, index_col=self.groupby,title=self.title,legend_placement=self.legend_placement,
                        bgcolor=self.bgcolor,legend_orientation=self.legend_orientation,legend_font_size=self.legend_font_size,
                        dimensions=self.dimensions,annotation_font_size=self.annotation_font_size,annotation_prefix=self.annotation_prefix,
                        annotation_suffix = self.annotation_suffix,
                        decimals=self.decimals,decimal_places=self.decimal_places,margin=self.margin,hole_size=self.hole_size,
                        line_width=self.line_width,font_family=self.font_family,font_color=self.font_color,directory=self.directory,colors=self.colors,show_legend=self.show_legend,text_font_size=self.text_font_size,
                        textinfo=self.textinfo,file_type = self.file_type,texttemplate=self.texttemplate,annotation=self.annotations, font_size=self.font_size)
        self.fig = fig
        return fig

    def ranked_bar_plot(self):
        print("Generating ranked bar plot...")
        # print(f'sort_list vis pipe: {self.sort_list}')
        # print(f'df sort order before ranked bar funct: {self.df[self.groupby].unique()}')
        fig = ranked_bar_chart(df=self.df,title=self.title, col=self.num_col, sort_col=self.groupby,
                     tickprefix=self.tick_prefix['y1'], ticksuffix=self.ticksuffix['y1'],
                     bgcolor=self.bgcolor, legend_orientation=self.legend_orientation, tickangle=self.tickangle, textposition=self.textposition, orientation=self.plot_orientation,
                     legend_placement=self.legend_placement, minsize=self.text_font_size, legend_font_size=self.legend_font_size,margin=self.margin,showlegend=self.show_legend,
                     decimals=self.decimals,traceorder=self.traceorder,decimal_places=self.decimal_places, to_reverse=self.to_reverse,discrete=self.discrete,
                     tickformat=self.tickformat['y1'],dimensions=self.dimensions,descending=self.descending,use_sort_list=self.sort_list,show_text=self.text,font_family=self.font_family,font_color=self.font_color
                    ,directory=self.directory,colors=self.colors,file_type = self.file_type,use_single_color=self.use_single_color, font_size=self.font_size)
        self.fig = fig
        return fig

    def save_fig(self, filetype='svg'):
        # Construct the full file path using os.path.join
        file_path = os.path.join(self.save_directory, f'{self.title}.{filetype}')

        print(f'Saving figure to: {file_path}')

        if filetype != 'html':
            # Save as image using Kaleido engine
            self.fig.write_image(file_path, engine="kaleido")
        else:
            # Save as HTML
            self.fig.write_html(file_path)

    def return_fig(self):
        # Check if self.fig is a Plotly Figure
        if isinstance(self.fig, go.Figure):  # Make sure you're using 'plotly.graph_objs' (go.Figure)
            return self.fig
        else:
            raise ValueError("The fig is not a valid Plotly Figure object.")

    def group_data(self,how='sum'):
        print(f'grouping by {self.groupby}... w/ {how}')
        if self.turn_to_time == False:
            if how == 'sum':
                self.df =  self.df.groupby(self.groupby)[self.num_col].sum().reset_index().sort_values(by=self.num_col,ascending=True)
                # print(f'{self.df}')
            elif how == 'mean':
                self.df = self.df.groupby(self.groupby)[self.num_col].mean().reset_index().sort_values(by=self.num_col,ascending=True)
            elif how == 'median':
                self.df = self.df.groupby(self.groupby)[self.num_col].median().reset_index().sort_values(by=self.num_col,ascending=True)
            elif how == 'last':
                self.df = self.df.groupby(self.groupby)[self.num_col].last().reset_index().sort_values(by=self.num_col,ascending=True)
                # print(f'{self.df}')
            elif how == 'first':
                self.df = self.df.groupby(self.groupby)[self.num_col].first().reset_index().sort_values(by=self.num_col,ascending=True)
                # print(f'{self.df}')
        else:
            if how == 'sum':
                self.df = self.df.groupby([self.df.index,self.groupby])[[self.num_col]].sum().reset_index().sort_values(by=self.num_col,ascending=True)
                self.df = to_time(self.df)
                self.df = self.df[0]
                # print(f'self.df @ groupby: {self.df}')
            elif how == 'mean':
                self.df = self.df.groupby(self.df.index)[self.num_col].mean().reset_index().sort_values(by=self.num_col,ascending=True)
            elif how == 'median':
                self.df = self.df.groupby(self.df.index)[self.num_col].median().reset_index().sort_values(by=self.num_col,ascending=True)
            elif how == 'last':
                self.df = self.df.groupby(self.df.index)[self.num_col].last().reset_index().sort_values(by=self.num_col,ascending=True)
                # print(f'{self.df}')
            elif how == 'first':
                self.df = self.df.groupby(self.df.index)[self.num_col].first().reset_index().sort_values(by=self.num_col,ascending=True)
                # print(f'{self.df}')

    def add_title(self,title=None,subtitle=None, x=None, y=None):
        # Add a title and subtitle
        if not hasattr(self, 'title_position') or self.title_position is None:
            self.title_position = {'x': None, 'y': None}

        # Update title position if values are provided
        if x is not None:
            self.title_position['x'] = x
        if y is not None:
            self.title_position['y'] = y

        # Update title and subtitle if provided
        # if title is not None:
        #     self.title = title
        # if subtitle is not None:
        #     self.subtitle = subtitle

        if title == None:
            title=""
        if subtitle == None:
            subtitle=""

        self.fig.update_layout(
            title={
                'text': f"<span style='color: black; font-weight: normal;'>{title}</span><br><sub style='font-size: 18px; color: black; font-weight: normal;'>{subtitle}</sub>",
                'y':1 if self.title_position['y'] == None else self.title_position['y'],
                'x':0.2 if self.title_position['x'] == None else self.title_position['x'],
                'xanchor': 'left',
                'yanchor': 'top',
                'font': {
                'color': 'black',  # Set the title color here
                'size': 27,  # You can also adjust the font size
                'family': self.font_family}
            },
        )

    def add_watermark(self):
        self.fig.add_layout_image(
            dict(
                source=self.watermark,
                x=0.5,  # Center horizontally
                y=0.5,  # Center vertically
                xref="paper",  # Reference to the paper coordinates
                yref="paper",  # Reference to the paper coordinates
                sizex=0.3,  # Size in x-direction (adjust as needed)
                sizey=0.3,  # Size in y-direction (adjust as needed)
                xanchor="center",  # Anchor point for x
                yanchor="middle",  # Anchor point for y
                # opacity=0.5,  # Adjust opacity for watermark effect
                layer="above"  # Place above other chart elements
            )
        )

    def add_dashed_line(self, date, annotation_text):
        # Ensure the date matches the index type
        if self.df.index.dtype == 'datetime64[ns]':
            date = pd.to_datetime(date)

        if date not in self.df.index:
            print(f"Error: {date} is not in the DataFrame index.")
            return

        # Validate number_col
        if self.num_col:
            number_col = self.num_col
            yvalue = self.df.loc[date, number_col].sum()
        else:
            # Validate cols_to_plot
            for col in self.cols_to_plot:
                if col not in self.df.columns:
                    print(f"Error: {col} is not in DataFrame columns.")
                    return
            
            # print(f'self.cols_to_plot: {self.cols_to_plot}')

            # breakpoint()

            self.df['max_value'] = self.df[self.cols_to_plot].max(axis=1)
            self.df['max_column'] = self.df[self.cols_to_plot].idxmax(axis=1)
            number_col = self.df['max_column'].iloc[0]  # Assume a valid column
            yvalue = self.df.loc[date, number_col]

            # print(f'number_col: {number_col}')
            # print(f'yvalue: {yvalue}')

        # Validate column and calculate value
        if number_col not in self.df.columns:
            print(f"Error: {number_col} is not a valid column in the DataFrame.")
            return

        # import pdb; pdb.set_trace()

        if pd.isna(yvalue):
            print(f"Warning: Missing value at {date} for {number_col}.")
            return

        # Add the dashed line and annotation
        self.fig.add_shape(
            type="line",
            x0=date,
            y0=0,
            x1=date,
            y1=yvalue*self.line_factor,
            line_dash="dot",
            line=dict(color="black", width=3),
        )
        self.fig.add_annotation(
            x=date,
            y=yvalue*self.line_factor,
            text=f"{annotation_text}<br>{pd.to_datetime(date).strftime(datetime_format)}",
            showarrow=False,
            font=dict(size=self.text_font_size, family=self.font_family, color="black"),
        )




    def add_logo(self):
        # Set the logo as a layout image
        self.fig.update_layout(
            images=[
                dict(
                    source=self.logo,  # Path to the logo
                    x=0.01,  # Lower-left corner horizontally
                    y=-0.1,  # Position in the lower margin vertically (adjust this value)
                    xref="paper",  # Reference to the paper coordinates
                    yref="paper",  # Reference to the paper coordinates
                    sizex=0.1,  # Size in x-direction (adjust as needed)
                    sizey=0.1,  # Size in y-direction (adjust as needed)
                    xanchor="left",  # Anchor point for x
                    yanchor="bottom",  # Anchor point for y
                    opacity=1,  # Fully opaque
                    layer="above"  # Place above other chart elements
                )
            ]
        )

    def add_horizontal_line_below_plot(self, y_value=-0.1, image_width=1):
        # Add a horizontal line below the plot area
        self.fig.add_shape(
            type="line",
            x0=0,  # Start point x (0 to 1 for paper coordinates)
            y0=y_value,  # Start point y (below the plot)
            x1=image_width,  # End point x (0 to 1 for paper coordinates)
            y1=y_value,  # End point y (same as y0 to create a horizontal line)
            line=dict(
                color="#CEC9C8",  # Line color
                width=3,      # Line width
                dash="solid"   # Line style (e.g., 'solid', 'dash', 'dot')
            ),
            xref="paper",  # Reference to paper coordinates
            yref="paper"   # Reference to paper coordinates for y
        )

    def add_date(self,date=None,x=0.5,y=1.1,dt_index=True):
        if not hasattr(self, 'date_position') or self.date_position is None:
            self.date_position = {'x': None, 'y': None}

        if x is not None:
            self.date_position['x'] = x
        if y is not None:
            self.date_position['y'] = y

        if date == None and dt_index==True:
            data_date = self.df.index[-1].strftime(datetime_format)
        elif date == None and dt_index == False:
            data_date = self.df.index[-1]
        elif date:
            data_date = pd.to_datetime(date).strftime(datetime_format)

        self.fig.add_annotation(
            text=data_date,
            xref='paper',  # Use paper coordinates
            yref='paper',
            x=0.5 if self.date_position['x'] == None else self.date_position['x'],  # Centered horizontally
            y=1.1 if self.date_position['y'] == None else self.date_position['y'],  # Slightly above the top of the plot
            showarrow=False,  # No arrow
            font=dict(size=self.legend_font_size, color='black'),  # Customize font size and color
            align='center'  # Center align the text
        )

    def chartBuilder(self, fig=None, title=None,subtitle=None,title_xy=dict(x=0.1,y=0.9),date_xy=dict(x=0.05,y=1.02),
         save=True,file_type='svg',clean_columns=False, capwords=None,
         show=True,show_index_and_cols=False,clean_values=False,clean_words=None,dt_index=True,add_the_date=True,groupby=False,groupbyHow='sum',
         date=None,dashed_line=False,annotation_text=None,axis='y1'):
        
        """
        Method to create the chart.

        Args:
            fig (go.Figure, optional): The Plotly figure object to use for the chart. If not provided, it will check for an existing figure.
            title (str, optional): The title of the chart. If not provided, it will use the default title.
            subtitle (str, optional): The subtitle of the chart. If not provided, it will use the default subtitle.
            title_xy (dict, optional): The x and y coordinates for the title. Defaults to dict(x=0.1, y=0.9).
            date_xy (dict, optional): The x and y coordinates for the date. Defaults to dict(x=0.05, y=1.02).
            save (bool, optional): Whether to save the chart. Defaults to True.
            file_type (str, optional): The file type to save the chart as. Defaults to 'svg'.
            clean_columns (bool, optional): Whether to clean the column names. Defaults to False.
            dt_index (bool, optional): Whether to use the DataFrame index as the x-axis. Defaults to True.
            add_the_date (bool, optional): Whether to add the date annotation to the chart. Defaults to True and uses the last date in the DataFrame.
            date (str, optional): The date to annotate on the chart. If not provided, it will use the last date in the DataFrame.
            dashed_line (bool, optional): Whether to add a dashed line to the chart. Defaults to False.
            annotation_text (str, optional): The text to annotate on the chart. Defaults to None.

        """

        if fig is None:
            fig = self.fig

        # print(f'save:{save}')
        
        if clean_values == True:
            fig.clean_values()

        if groupby:
            fig.group_data(how=groupbyHow)

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

    # def get_submissions_data(self,start_date, end_date,submission_num=0):
    #     dataPipeline = data_pipeline()
    #     # submissions_data = dataPipeline.get_submissions(start_date=start_date,end_date=end_date)
    #     # submission = get_submission_df(submissions_data, submission_num)
    #     # project = submission['project']
    #     # files = get_files(submission)
    #     # file=f'{submission_directory}/{files["first_file"]}',
    #     # show_file_and_img(submission,index=submission_num)


        



        






    

        