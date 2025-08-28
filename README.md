# A Library for High-Quality, Reproducable Charts

- This library builds off Plotly and automates portions of data cleaning and charting for users.
- A user only inputs specified parameters such as chart type and columns to chart, enabling quick charting of complex data structures.

# Visualization Pipeline Parameters

This document explains the parameters of the `visualization_pipeline` class, grouped by category.

---

## 1. Core Settings

- **chart_type**: Type of chart (`line`, `bar`, `pie`, `line_and_bar`, `ranked bar`, etc.).
- **title**: Chart title.
- **subtitle**: Chart subtitle.
- **auto_title**: If `True`, automatically generates a title using column names.
- **dimensions**: Dict with chart size, e.g. `dict(height=400, width=730)`.
- **bgcolor**: Background color (`rgba` string).
- **autosize**: If `True`, chart auto-scales to container.

---

## 2. Data Input & Processing

- **df**: Pandas DataFrame containing the data.
- **file**: File path to load data from (optional).
- **is_file_path**: If `True`, treats `file` as a path to read from.
- **delimiter**: File delimiter (e.g., `,`).
- **cols_to_plot**: Columns to include (`'All'` by default).
- **groupby**: Column used for grouping data.
- **num_col**: Numeric column used for y-axis values.
- **bar_col / line_col**: Set the columns used for charting in a `line_and_bar` chart type.
- **index_col**: Column to use as DataFrame index.
- **time_col**: Column to treat as datetime.
- **set_time_col**: Sets the estimated datetime column as index, but does NOT turn to datetime data type.
- **turn_to_time**: If `True`, converts `time_col` to datetime.
- **resample_freq**: Resampling frequency (`'D'`, `'W'`, `'M'`).
- **agg_func**: Aggregation function (`'sum'`, `'mean'`, etc.).
- **start_date / end_date**: Filters data within a date range.
- **drop_duplicates**: Drop duplicate rows if `True`.
- **fillna / ffill**: Fill missing values.
- **keepna / dropna / dropna_col**: NA handling options.
- **clean_dates**: If `True`, will drop latest data points in timeseries if it falls within the middle of the estimated time frequency (week, month, year).

---

## 3. Axes & Ticks

- **axes_data**: Dict specifying axes data, e.g. `dict(y1=[], y2=[])`.
- **axes_titles**: Dict with axis titles, e.g. `dict(y1="Y Axis", y2="Secondary Y Axis")`.
- **axes_font_colors**: Dict of axis font colors (`y1`, `y2`). Also take in `auto` to automatically use the color palette.
- **tick0**: Starting tick value (`'min'` for auto).
- **dtick**: Step size between ticks.
- **tickformat**: Dict for axis formatting, e.g. `dict(x='%b %d <br>%y')`.
- **tickprefix**: Dict of prefixes for axis ticks (`y1`, `y2`).
- **ticksuffix**: Dict of suffixes for axis ticks (`y1`, `y2`).
- **tickangle**: Angle of tick labels.
- **ytickvals**: Custom y-axis tick values.
- **yticktext**: Custom y-axis tick labels.
- **ytick_num**: Number of y-axis ticks.
- **custom_ticks**: Apply custom tick formatting.
- **min_tick_spacing**: Minimum spacing between ticks.
- **remove_zero**: If `True`, removes zero from axis.
- **y_log**: Logarithmic y-axis if `True`.

---

## 4. Sorting & Data Presentation

- **sort_list**: If `True`, sort categories automatically.
- **user_sort_list**: Custom list defining sort order.
- **descending**: Sort order (descending if `True`).
- **cumulative_sort**: If `True`, will sort data series using total sum.
- **to_reverse**: Reverse sort order if `True`.
- **topn**: Limit to top N values.
- **normalize**: Normalize values to percentage if `True`.
- **to_percent**: Multiply values by 100 to turn from decimal to percent.

---

## 5. Visual Styling

- **colors**: Color palette.
- **user_color_map**: Map specific values → colors.
- **use_single_color**: Force single-color scheme if `True`.
- **line_color**: Line color used in the `line_and_bar` chart type.
- **marker_col / y2_col**: Columns for color or dual-axis mapping.
- **marker_size**: Size of scatter markers.
- **line_width**: Width of line traces.
- **line_factor**: Line scaling factor for a vertical dashed line.
- **area**: Fill under line if `True`.
- **fill**: Plotly fill type (`tozeroy`, `tonexty`, etc.).
- **barmode**: Bar mode (`stack`, `group`, etc.).
- **orientation**: Chart orientation (`'v'` vertical, `'h'` horizontal).
- **mode**: Trace mode (`lines`, `markers`, etc.).
- **traceorder**: Legend item order (`'normal'`, `'reversed'`).
- **discrete**: If `True`, treats values as discrete.

---

## 6. Text & Labels

- **text**: Show text labels if `True`.
- **text_freq**: Frequency of text labels.
- **textposition**: Label position (`inside`, `outside`, etc.).
- **text_font_size**: Font size for labels.
- **texttemplate**: Custom text template for labels.
- **textinfo**: For pie charts (`'percent+label'`, etc.).
- **annotation_prefix / annotation_suffix**: Prefix/suffix for annotation values.
- **annotations**: If `True`, show annotations for first and last data point.
- **max_annotation**: If `True`, show annotation for the highest value in the data.
- **custom_annotation**: Custom annotation text.
- **annotation_font_size**: Font size of annotations.

---

## 7. Legend & Layout

- **show_legend**: Show legend if `True`.
- **legend_orientation**: Orientation (`'v'` vertical, `'h'` horizontal).
- **legend_placement**: Dict for placement (`dict(x=0.2, y=0.9)`).
- **legend_font_size**: Font size of legend text.
- **legend_background**: Dict for legend box (bgcolor, border, etc.).
- **itemsizing**: Legend item sizing (`'constant'`, `'trace'`).
- **margin**: Chart margins (l, r, t, b).

---

## 8. Fonts & Theming

- **font_size**: Global font size.
- **font_family**: Font family (default: `'Cardo'`).
- **font_color**: Font color.
- **logo**: Path to logo overlay.

---

## 9. Export & Saving

- **directory / save_directory**: Output directory for saved images.
- **file_type**: Export type (`'svg'`, `'png'`, etc.).
- **buffer**: When the index is datetime type, this will add a buffer to the x axis with either integer or float used to represent number of days.
- **hole_size**: Pie/donut hole size (0–1).
- **days_first**: Parses datetime column assuming days occur first in the string.

---
