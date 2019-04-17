# Clinical-Trials
# Mary made this by using https://towardsdatascience.com/data-visualization-with-bokeh-in-python-part-iii-a-complete-dashboard-dc6a86aa6e23
# as a model

# Pandas for data management
import pandas as pd

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs


# Each tab is drawn by one script
from scripts.histogram import histogram_tab
# from scripts.density import density_tab
from scripts.table import table_tab
# from scripts.draw_map import map_tab
# from scripts.routes import route_tab

# Using included state data from Bokeh for map
# from bokeh.sampledata.us_states import data as states

# Read data into dataframes
trials = pd.read_csv(join(dirname(__file__), 'data', 'SearchResults.csv'),
	                                          index_col=0).dropna(subset=['Phases', 'Enrollment'])

# Formatted Flight Delay Data for map
# map_data = pd.read_csv(join(dirname(__file__), 'data', 'flights_map.csv'),
                            # header=[0,1], index_col=0)

# Create each of the tabs
tab1 = histogram_tab(trials)
# tab2 = density_tab(flights)
tab3 = table_tab(trials)
# tab4 = map_tab(map_data, states)
# tab5 = route_tb(flights)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1, tab3])
# tabs = Tabs(tabs = [tab1, tab2, tab3, tab4, tab5])

# Put the tabs in the current document for display
curdoc().add_root(tabs)
