# Clinical-Trials
# Mary made this by using https://towardsdatascience.com/data-visualization-with-bokeh-in-python-part-iii-a-complete-dashboard-dc6a86aa6e23
# as a model

# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool,
						  ColumnDataSource, Panel,
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider,
								  Tabs, CheckboxButtonGroup,
								  TableColumn, DataTable, Select)
from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

# Make plot with histogram and return tab
def histogram_tab(trials):

	# Function to make a dataset for histogram based on a list of carriers
	# a minimum delay, maximum delay, and histogram bin width
	def make_dataset(phase_list, range_start = 0, range_end = 1000, bin_width = 500):

		# Dataframe to hold information
		by_phase = pd.DataFrame(columns=['proportion', 'left', 'right',
										   'f_proportion', 'f_interval',
										   'name', 'color'])

		range_extent = range_end - range_start

		print(phase_list)
		# Iterate through all the carriers
		for i, phase_name in enumerate(phase_list):

			# Subset to the carrier
			subset = trials[trials['Phases'] == phase_name]

			# Create a histogram with 5 minute bins
			enrollment_hist, edges = np.histogram(subset['Enrollment'],
										   bins = int(range_extent / bin_width),
										   range = [range_start, range_end])
			print(enrollment_hist)
			print(edges)

			# Divide the counts by the total to get a proportion
			enrollment_df = pd.DataFrame({'proportion': enrollment_hist / np.sum(enrollment_hist), 'left': edges[:-1], 'right': edges[1:] })

			# Format the proportion
			enrollment_df['f_proportion'] = ['%0.5f' % proportion for proportion in enrollment_df['proportion']]

			# Format the interval
			enrollment_df['f_interval'] = ['%d to %d enrollees' % (left, right) for left, right in zip(enrollment_df['left'], enrollment_df['right'])]

			# Assign the carrier for labels
			enrollment_df['name'] = phase_name

			# Color each carrier differently
			enrollment_df['color'] = Category20_16[i]

			# Add to the overall dataframe
			by_phase = by_phase.append(enrollment_df)

		# Overall dataframe
		by_phase = by_phase.sort_values(['name', 'left'])

		return ColumnDataSource(by_phase)

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

		return p

	def make_plot(src):
		# Blank plot with correct labels
		p = figure(plot_width = 700, plot_height = 700,
				  title = 'No. of Patients Enrolled by NICHD-sponsored Trials',
				  x_axis_label = 'Enrollment', y_axis_label = 'Proportion')

		# Quad glyphs to create a histogram
		p.quad(source = src, bottom = 0, top = 'proportion', left = 'left', right = 'right',
			   color = 'color', fill_alpha = 0.7, hover_fill_color = 'color', legend = 'name',
			   hover_fill_alpha = 1.0, line_color = 'black')

		# Hover tool with vline mode
		hover = HoverTool(tooltips=[('Phase', '@name'),
									('Enrollment', '@f_interval'),
									('Proportion', '@f_proportion')],
						  mode='vline')

		p.add_tools(hover)

		# Styling
		p = style(p)

		return p



	def update(attr, old, new):
		phases_to_plot = [phase_selection.labels[i] for i in phase_selection.active]

		new_src = make_dataset(phases_to_plot,
							   range_start = range_select.value[0],
							   range_end = range_select.value[1],
							   bin_width = binwidth_select.value)



		src.data.update(new_src.data)

	# Carriers and colors
	available_phases = list(set(trials['Phases']))
	available_phases.sort()


	airline_colors = Category20_16
	airline_colors.sort()

	phase_selection = CheckboxGroup(labels=available_phases,
									  active = [1, 2])
	phase_selection.on_change('active', update)

	binwidth_select = Slider(start = 0, end = 500,
							 step = 1, value = 50,
							 title = 'Bin Width (min)')
	binwidth_select.on_change('value', update)

	range_select = RangeSlider(start = 0, end = 10000, value = (100, 500),
							   step = 50, title = 'Range of Enrollment')
	range_select.on_change('value', update)

	# Initial carriers and data source
	initial_phases = [phase_selection.labels[i] for i in phase_selection.active]

	src = make_dataset(initial_phases,
					   range_start = range_select.value[0],
					   range_end = range_select.value[1],
					   bin_width = binwidth_select.value)
	p = make_plot(src)

	# Put controls in a single element
	controls = WidgetBox(phase_selection, binwidth_select, range_select)

	# Create a row layout
	layout = row(controls, p)

	# Make a tab with the layout
	tab = Panel(child=layout, title = 'Histogram')

	return tab
