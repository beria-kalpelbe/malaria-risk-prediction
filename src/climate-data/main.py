import json

with open("../utils/cdsapi-client.json", "r") as f:
    cdsapi_data = json.load(f)

url = cdsapi_data["url"]
key = cdsapi_data["key"]

from climate_data import ClimateData

dataset = ClimateData(url=url, key=key)
dataset.run()
dataset.save_data()