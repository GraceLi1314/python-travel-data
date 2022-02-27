import pandas as pd
import requests
import json
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="main.py")
location = geolocator.geocode("Ice Palace of Jungfraujoch, Switzerland")
print(location.latitude, location.longitude)