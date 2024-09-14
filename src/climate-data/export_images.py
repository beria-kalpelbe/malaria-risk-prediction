import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd


def display_in_map(data, column, limits):
    fig, ax = plt.subplots(1, figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    data.plot(edgecolor='none', ax=ax, column=column, cmap='coolwarm', 
              legend=False, vmin=limits[column][0], vmax=limits[column][1])
    plt.legend('')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

def get_min_max(data_path:str='../../data/panel_data.csv'):
    data = pd.read_csv(data_path)
    return {
        'cases': (data['cases'].min(), data['cases'].max()),
        't2m': (data['t2m'].min(), data['t2m'].max()),
        'tp': (data['tp'].min(), data['tp'].max())
    }
    
    
times = [f'{year}-{month:02d}-01' for year in range(2020,2023) for month in range(1,13)]
root_images = '../../data/images/'

limits = get_min_max()
for time in times:
    data_map = gpd.read_file(f'../../data/preprocessed_data/{time}.geojson')
    display_in_map(data_map, 'cases', limits)
    plt.axis('off')
    plt.savefig(f'{root_images}cases-{time}.png', format='png', bbox_inches='tight', pad_inches=0, dpi=50)
    display_in_map(data_map, 't2m', limits)
    plt.axis('off')
    plt.savefig(f'{root_images}t2m-{time}.png', format='png', bbox_inches='tight', pad_inches=0, dpi=50)
    display_in_map(data_map, 'tp', limits)
    plt.axis('off')
    plt.savefig(f'{root_images}tp-{time}.png', format='png', bbox_inches='tight', pad_inches=0, dpi=50)
    