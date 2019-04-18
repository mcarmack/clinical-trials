
# time.py
# Plot the trials by year of publication
# Y axis- year of publication
# x axis - start year
# color - phase
# size - number enrolled
# include with checkboxes: status

import pandas as pd
import numpy as np
import re
from types import *

from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool,
						  ColumnDataSource, Panel,
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider,
								  Tabs, CheckboxButtonGroup,
								  TableColumn, DataTable, Select)
from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Spectral6

def get_year_from_string(str_date):
    # return year from string or else 2030
    match = re.match(r'.*([1-2][0-9]{3})', str(str_date))
    if match is not None:
        return match.group(1)
    else:
        # no year found in the string
        return 2025

def get_circle_size(enrollment):
    # Turn enrollment into bubble sizes. Use min_size and factor to tweak.
    count = int(enrollment)
    scale_factor = .5
    min_size = 5
    raw_size = np.sqrt(count / np.pi) / scale_factor
    pretty_size = raw_size if raw_size >= min_size else min_size
    return pretty_size

def time_tab(trials):
	# Function to make a dataset for histogram based on a list of carriers
	# a minimum delay, maximum delay, and histogram bin width
    def make_dataset(phases_to_plot, statuses_to_plot, range_start = 0, range_end = 10000):
        # Dataframe to hold information
        range_extent = range_end - range_start
        by_phase_subset = pd.DataFrame(columns=['enrollment', 'phases', 'status', 'title',
                                         'enrollment_size', 'start_year',
                                         'results_year', 'color'])

        for i, phase_name in enumerate(phases_to_plot):
            for j, status_name in enumerate(statuses_to_plot):
                # Subset to the phase
                subset = trials[trials['Phases'] == phase_name]
                subset = subset[subset['Status'] == status_name]
                subset = subset[subset['Enrollment'] <= range_end]
                subset = subset[subset['Enrollment'] >= range_start]

                enrollment_df = pd.DataFrame({'enrollment': subset['Enrollment']})
                enrollment_df['phases'] = phase_name
                enrollment_df['status'] = subset['Status']
                enrollment_df['title'] = subset['Title']

                # Color each carrier differently
                enrollment_df['color'] = Spectral6[i]

                enrollment_df['start_year'] = subset['Start Date'].apply(get_year_from_string)
                enrollment_df['results_year'] = subset['Results First Posted'].apply(get_year_from_string)

                enrollment_df['start_date'] = subset['Start Date']
                enrollment_df['results_date'] = subset['Results First Posted']

                # Turn enrollment into bubble sizes. Use min_size and factor to tweak.
                enrollment_df['enrollment_size'] = enrollment_df['enrollment'].apply(get_circle_size)

                by_phase_subset = by_phase_subset.append(enrollment_df)

        # Overall dataframe
        by_phase_subset = by_phase_subset.sort_values(['phases'])

        return ColumnDataSource(by_phase_subset)

    def style(p):
        # Title
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'

    	# Axis titles
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'

        p.legend.location = "bottom_left"

        return p

    def make_plot(src):
        # Blank plot with correct labels
        p = figure(plot_width = 1000, plot_height = 700, title = 'Trials Sponsored by NICHD', x_axis_label = 'Start Year', y_axis_label = 'Year of First Results Posting')

        # Circle markers
        p.circle(source = src, x = 'start_year', y = 'results_year',
                 size = 'enrollment_size', color = 'color',
                 fill_alpha = 0.7, line_color = 'black', legend = 'phases')

        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('Title', '@title'),
                                    ('Phase', '@phases'),
                                    ('Enrollment', '@enrollment'),
                                    ('Start Date', '@start_date'),
                                    ('First Results Posted Date', '@results_date'),
                                    ('Status', '@status')], mode='mouse')

        p.add_tools(hover)
        p = style(p)

        return p

    def update(attr, old, new):
        phases_to_plot = [phase_selection.labels[i] for i in phase_selection.active]
        statuses_to_plot = [status_selection.labels[i] for i in status_selection.active]

        new_src = make_dataset(phases_to_plot, statuses_to_plot, range_start = range_select.value[0], range_end = range_select.value[1])


        src.data.update(new_src.data)

    # Phases and colors
    available_phases = list(set(trials['Phases']))
    available_phases.sort()

    available_statuses = list(set(trials['Status']))
    available_statuses.sort()

    phase_colors = Spectral6
    phase_colors.sort()

    phase_selection = CheckboxGroup(labels=available_phases, active = [2,4,6,7])
    phase_selection.on_change('active', update)

    status_selection = CheckboxGroup(labels=available_statuses, active = [1])
    status_selection.on_change('active', update)

    range_select = RangeSlider(start = 0, end = 10000, value = (100, 500), step = 50, title = 'Range of Enrollment')
    range_select.on_change('value', update)

    # Initial carriers and data source
    initial_phases = [phase_selection.labels[i] for i in phase_selection.active]
    initial_statuses = [status_selection.labels[i] for i in status_selection.active]

    src = make_dataset(initial_phases, initial_statuses, range_start = range_select.value[0], range_end = range_select.value[1])
    p = make_plot(src)

    # Put controls in a single element
    controls = WidgetBox(phase_selection, status_selection, range_select)

    # Create a row layout
    layout = row(controls, p)

    # Make a tab with the layout
    tab = Panel(child=layout, title = 'Time Plot')

    return tab
