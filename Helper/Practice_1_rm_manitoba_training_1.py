import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display

df_yield_raw=pd.read_excel('/Users/Roy/Desktop/PaletteSkills/Stream-3__AI_ML_Doc/Python_Class_Practice/data/rm_mb_yield_2004_2023.xlsx')
gdf_rm=gpd.read_file('/Users/Roy/Desktop/PaletteSkills/Stream-3__AI_ML_Doc/Python_Class_Practice/data/MUNICIPALITY.geojson', engine="pyogrio")

# Dropping Unncesseary Columns
df_yield_raw_1=df_yield_raw.drop(columns=['Variety', 'Yield/acre(Metric)', 'Yield/acre(Metric).1', 'Yield/acre(Imperial).1' ])
# Creating new clean yield column
df_yield_raw_1['Yield']=df_yield_raw_1['Yield/acre(Imperial)'].str.replace(' Bushels','')

# Dropping old yield column
df_yield_raw_2=df_yield_raw_1.drop(columns='Yield/acre(Imperial)')


# Removing observations that have not enough values
df_yield_raw_3=df_yield_raw_2.loc[df_yield_raw_2['Farms']!='Below']
# Changing column names
df_yield_raw_3=df_yield_raw_3.rename(columns={'Risk Area / R.M.': 'RM'})
gdf_rm=gdf_rm.rename(columns={'MUNI_LIST_NAME': 'RM'})

print('Number of RMs in GIS data:',gdf_rm['RM'].nunique())
print('Number of RMs in Yield Data:', df_yield_raw_3['RM'].nunique())

# Joining two tables - GIS/Yield
gdf_rm_join_1=pd.merge(df_yield_raw_3, gdf_rm, on='RM', how='inner')\
    .drop(columns=[ 'OBJECTID', 'MUNI_NO',
       'MUNI_NAME', 'MUNI_TYPE', 'MUNI_LIST_NAME_WITH_TYPE'])

# From DataFrame to GeoDataFrame
gdf_yield=gpd.GeoDataFrame(gdf_rm_join_1)
# Change data type to float or numerical from object
gdf_yield['Yield']=gdf_yield['Yield'].astype(float)

print('Number of RMs after merging: ',gdf_rm_join_1['RM'].nunique() )
print(gdf_yield)

gdf_yield.loc[(gdf_yield['Year']==2023) &( gdf_yield['Crop']=='BARLEY')]\
    .explore('Yield', cmap='RdYlGn')

#Function to create and display the map based on crop selection
def create_map(crop):
    # Filter the GeoDataFrame for the selected crop
    filtered_gdf = gdf_yield.loc[(gdf_yield['Year'] == 2023) & (gdf_yield['Crop'] == crop)]
    
    # Use explore() from geopandas to display the filtered GeoDataFrame interactively
    return filtered_gdf.explore(column='Yield', cmap='RdYlGn', legend=True)

# Dropdown widget to select a crop
crop_selector = widgets.Dropdown(
    options=['BARLEY', 'OATS', 'RED SPRING WHEAT', 'ARGENTINE CANOLA'],
    value='BARLEY',
    description='Select Crop:',
)

# Output widget to display the map
output = widgets.Output()

# Function to update the map when a different crop is selected
def update_map(change):
    with output:
        output.clear_output()  # Clear previous map output
        m = create_map(crop_selector.value)  # Generate the new map
        display(m)

# Trigger map update when the dropdown changes
crop_selector.observe(update_map, names='value')

# Display dropdown and initial map
display(crop_selector)
update_map(None)  # Initialize with the first map
display(output)