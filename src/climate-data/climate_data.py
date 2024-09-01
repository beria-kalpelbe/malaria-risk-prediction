import cdsapi
import calendar
import xarray as xr
import os
import pickle

class ClimateData:
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.data = {}
        self.client = cdsapi.Client(url=url, key=key)

    def _get_number_of_days(self, year: int, month: int) -> int:
        return calendar.monthrange(year, month)[1]
    
    def _get_number_months(self, year: int):
        return 12 if year<2024 else 7
    
    def _delete_datafile(self, file_path:str="data.nc"):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"File '{file_path}' does not exist.")

    
    def _extract_data_time(
            self, 
            variable_name:str, 
            variable_code:str, 
            year:str, 
            month:str, 
            day:str, 
            time:str, 
            area=[23.5, 13.5, 7.0, 24.0], #[35, -20, -35, 50], 
            format='netcdf', 
            filename='data.nc'
        ):
        client = cdsapi.Client(url=self.url, key=self.key)
        client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': variable_name,
                'year': year,
                'month': month,
                'day': day,
                'time': time,
                'format': format,
                'area': area,  # [north, west, south, east] for Africa
            },
            filename)
        if variable_code not in self.data.keys():
            self.data[variable_code] = {}
        if year not in self.data[variable_code].keys():
            self.data[variable_code][year] = {}
        if month not in self.data[variable_code][year].keys():
            self.data[variable_code][year][month] = {}
        if day not in self.data[variable_code][year][month].keys():
            self.data[variable_code][year][month][day] = {}
        data = xr.open_dataset('data.nc')
        self.data[variable_code][year][month][day][time] = data[variable_code].sel(time=f'{year}-{month}-{day}T{time}:00')
        
    
    def _extract_data_day(
            self, 
            variable_name:str, 
            variable_code:str, 
            year:str, 
            month:str, 
            day:str, 
        ):
        # for time in [f"{hour:02d}:00" for hour in range(0,24)]:
        self._extract_data_time(
                variable_name=variable_name,
                variable_code=variable_code,
                year=year,
                month=month,
                day=day,
                time='12:00' #time
        )
    
    def _extract_data_month(
        self,
        variable_name:str,
        variable_code:str,
        year:str,
        month:str
    ):
        # for day in range(1, self._get_number_of_days(year=int(year), month=int(month))+1):
        self._extract_data_day(
                variable_name=variable_name,
                variable_code=variable_code,
                year=year,
                month=month,
                day=f"{15:02d}"
        )
        print(f"\n\n===============Extracted data for year:{year} and month:{month}=====================\n\n")
    
    def _extract_data_year(
        self,
        variable_name:str,
        variable_code:str,
        year:str
    ):
        for month in range(1, self._get_number_months(int(year))):
            self._extract_data_month(
                variable_name=variable_name,
                variable_code=variable_code,
                year=year,
                month=f"{month:02d}"
            )

    def _extract_data(
        self,
        variable_name:str,
        variable_code:str,
        years:list[str], # min=1940, max=2024
    ):
        for year in years:
            self._extract_data_year(
                variable_name=variable_name,
                variable_code=variable_code,
                year=year
            )
    
    def _extract_all_data(self):
        variables_names=[
                '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                '2m_temperature', 'mean_sea_level_pressure', 'mean_wave_direction',
                'mean_wave_period', 'sea_surface_temperature', 'significant_height_of_combined_wind_waves_and_swell',
                'surface_pressure', 'total_precipitation',
            ],
        variables_codes = ['u10', 'v10', 'd2m', 't2m', 'msl', 'mwd', 'mwp', 'sst', 'swh', 'sp', 'tp']
        for i in range(len(variables_names)):
            self._extract_data(
                variable_name=variables_names[i],
                variable_code=variables_codes[i],
                years=[str(yr) for yr in range(2000,2025)], # min=1940, max=2023
            )
    
    def _save_data(self, file_path:str="../../data/data.pkl"):
        with open(file_path, "wb") as f:
            pickle.dump(self.data, f)
    
    def run(self):
        self._extract_all_data()
        self._save_data()