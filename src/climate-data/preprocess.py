import xarray as xr
import numpy as  np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from tqdm import tqdm

original_climate_data = xr.open_dataset('../../data/chad-data-climate.nc')
malaria_data = pd.read_excel('../../data/malaria-data.xlsx')
malaria_data = malaria_data.drop(columns=['Health district/hospital'])
malaria_data = malaria_data.groupby(['year','month','region']).sum().reset_index()
malaria_data = malaria_data.rename(columns={'region':'state'})

def aggregate_data(data_raster, var_name, time, data, map_data):
        vars = data_raster[var_name].sel(valid_time=time)
        for index in range(len(map_data['shapeName'])):
            var = []
            for lat in data_raster.latitude:
                for lon in data_raster.longitude:
                    point = Point(lon, lat)
                    if point.within(map_data.geometry[index]):
                        x, y = np.where(vars.latitude.values == lat.values.item())[0][0], np.where(vars.longitude.values == lon.values.item())[0][0]
                        var.append(vars.values[x, y].item())
            data.loc[index, var_name] = np.mean(var).item() - 273.15 # Convert to Celsius
        return data
    
map_data = gpd.read_file('../../data/chadgeodata/geoBoundaries-TCD-ADM1-all/geoBoundaries-TCD-ADM1.geojson')

malaria_data['state'] = malaria_data['state'].replace('BEG', 'BAHR EL GAZEL')
malaria_data['time'] = [f'{malaria_data['year'][i]}-{malaria_data['month'][i]:02d}-01' for i in range(len(malaria_data['year']))]
malaria_data = malaria_data.drop(columns=['year', 'month'])

data_to_csv = pd.DataFrame()
for time in tqdm(original_climate_data.valid_time, desc="Aggregating climate data"):
    map_data = gpd.read_file('../../data/chadgeodata/geoBoundaries-TCD-ADM1-all/geoBoundaries-TCD-ADM1.geojson')
    climate_data = pd.DataFrame(map_data['shapeName'], columns=['time','shapeName','t2m', 'tp', 'lai_hv', 'lai_lv'])
    climate_data = aggregate_data(original_climate_data, 't2m', str(time.values),climate_data, map_data)
    climate_data = aggregate_data(original_climate_data, 'tp', str(time.values), climate_data, map_data)
    climate_data = aggregate_data(original_climate_data, 'lai_hv', str(time.values), climate_data, map_data)
    climate_data = aggregate_data(original_climate_data, 'lai_lv', str(time.values), climate_data, map_data)
    climate_data['time'] = [str(time.values).split('T')[0]]*23
    # climate_data = pd.concat([climate_data, d], axis=0)
    # climate_data.reset_index(drop=True, inplace=True)

    climate_data = climate_data.rename(columns={'shapeName':'state'})
    climate_data['state'] = climate_data['state'].str.upper()
    climate_data['state'] = climate_data['state'].replace('ENNEDI-OUEST', 'ENNEDI OUEST')
    climate_data['state'] = climate_data['state'].replace('OUADDAÏ', 'OUADDAI')
    climate_data['state'] = climate_data['state'].replace('GUÉRA', 'GUERA')
    climate_data['state'] = climate_data['state'].replace('HADJER-LAMIS', 'HADJER LAMIS')
    climate_data['state'] = climate_data['state'].replace('CHARI-BAGUIRMI', 'CHARI BAGUIRMI')
    climate_data['state'] = climate_data['state'].replace('MAYO KEBBI EST', 'MAYO KEBBI EST')
    climate_data['state'] = climate_data['state'].replace('MAYO-KEBBI OUEST', 'MAYO KEBBI OUEST')
    climate_data['state'] = climate_data['state'].replace('MOYEN-CHARI', 'MOYEN CHARI')
    climate_data['state'] = climate_data['state'].replace('ENNEDI-EST', 'ENNEDI EST')
    climate_data['state'] = climate_data['state'].replace('TANDJILÉ', 'TANDJILE')
    climate_data['state'] = climate_data['state'].replace('MAYO-KEBBI EST', 'MAYO KEBBI EST')
    climate_data['state'] = climate_data['state'].replace("N'DJAMENA REGION", 'NDJAMENA')

    processed_data = pd.merge(climate_data, malaria_data)
    data_to_csv = pd.concat([data_to_csv, processed_data], axis=0)
    processed_data = processed_data[['state', 'time', 't2m', 'tp', 'lai_hv', 'lai_lv', 'cases','deaths']]

    map_data = map_data.rename(columns={'shapeName':'state'})

    map_data['t2m'] = processed_data['t2m']
    map_data['tp'] = processed_data['tp']
    map_data['lai_hv'] = processed_data['lai_hv']
    map_data['lai_lv'] = processed_data['lai_lv']
    map_data['cases'] = processed_data['cases']
    map_data['deaths'] = processed_data['deaths']

    map_data['t2m'] = map_data['t2m'].astype(np.float64)
    map_data['tp'] = map_data['tp'].astype(np.float64)
    map_data['lai_hv'] = map_data['lai_hv'].astype(np.float64)
    map_data['lai_lv'] = map_data['lai_lv'].astype(np.float64)

    map_data.to_file(f'../../data/preprocessed_data/{str(time.values).split('T')[0]}.geojson', driver='GeoJSON')

data_to_csv.to_csv('../../data/panel_data.csv', index=False)