# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import TableColumn, DataTable

def table_tab(trials):

	# Calculate summary stats for table
	phase_stats = trials.groupby('Phases')['Enrollment'].describe()
	print(phase_stats)
	phase_stats = phase_stats.reset_index().rename(
		columns={'name': 'Phases', 'count': 'trials', '50%':'median'})

	# Round statistics for display
	phase_stats['mean'] = phase_stats['mean'].round(2)
	phase_src = ColumnDataSource(phase_stats)

	# Columns of table
	table_columns = [TableColumn(field='Phases', title='Phases'),
					 TableColumn(field='trials', title='Number of Trials'),
					 TableColumn(field='min', title='Min Enrollment'),
					 TableColumn(field='mean', title='Mean Enrollment'),
					 TableColumn(field='median', title='Median Enrollment'),
					 TableColumn(field='max', title='Max Enrollment')]

	phase_table = DataTable(source=phase_src,
							  columns=table_columns, width=1000)

	tab = Panel(child = phase_table, title = 'Summary Table')

	return tab
