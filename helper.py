from googleplaces import GooglePlaces, types, lang
from geopy.distance import geodesic
import kml2geojson as k2g
import geopandas as gpd
import googlemaps
import pandas as pd
import requests
import os

API_KEY = "AIzaSyCwkzfZ-FtT_4aeL7utuPtvLXw4WoXQHkw"
google_places = GooglePlaces(API_KEY)
gmaps = googlemaps.Client(key=API_KEY)

def get_location(loc):
    target_keyword = loc
    geocode_result = gmaps.geocode(target_keyword)
    PLACE_ID = geocode_result[0]['place_id']

    url = f"https://maps.googleapis.com/maps/api/place/details/json?placeid={PLACE_ID}&key={API_KEY}"
    r = requests.get(url).json()
    lat, lng = r["result"]["geometry"]["location"]['lat'], r["result"]["geometry"]["location"]['lng']
    return lat, lng

def get_nearby_restaurants(lat, lng, nth=10):
    # 查找附近的餐厅
    google_places = GooglePlaces(API_KEY)
    query_result = google_places.nearby_search(
            lat_lng={'lat': lat, 'lng': lng}, 
            radius=2000,
            types=['restaurant'])

    candidate_dict = {}
    res = []
    for place in query_result.places:
        place.get_details()
        try:
            rating = float(place.details['rating'])
        except:
            rating = 0.
        candidate_dict[place.name] = (rating, float(place.details["geometry"]["location"]['lat']), float(place.details["geometry"]["location"]['lng']))

    candidate_dict = {k: v for k, v in sorted(candidate_dict.items(), key=lambda item: item[1][0], reverse=True)}
    # print("\nNearby restaurant:\n")
    for idx, (key, value) in enumerate(candidate_dict.items()):
        if idx >= nth:
            break
        res.append((key, value[0], value[1], value[2]))
        # print("{}th: {} rating: {}".format(idx+1, key, value[0]))
    return res


def get_distance(lat1, lng1, lat2, lng2):
    return (geodesic((lat1, lng1), (lat2, lng2)).m)

def get_nearest_carpark(lat, lng):
    print(os.getcwd())
    carpark_loc_df = pd.read_csv("/Users/shaozihang/Downloads/CS5224_frontend/backend/carpark_locations.csv")
    min_dist = float("inf")
    cloest_park = None
    for index, row in carpark_loc_df.iterrows():
        dist = get_distance(lat, lng, row['lat'], row['lng'])
        if dist < min_dist:
            min_dist = dist
            cloest_park = row['carpark_name']
    return cloest_park, min_dist

def search(keyword):
    lat, lng = get_location(keyword)
    restaurants_infos = get_nearby_restaurants(lat, lng, nth=10)
    recommendations = []
    for item in restaurants_infos:
        cloest_park, min_dist = get_nearest_carpark(item[2], item[3])
        recommendations.append({
            "restaurant_name": item[0], "restaurant_rating": item[1], "restaurant_lat": item[2], "restaurant_lng": item[3],
            "nearest_carpark": cloest_park, "min_dist": min_dist
        })

    return recommendations

# info = search("Commonwealth Crescent 108")
# for idx, i in enumerate(info):
#     print("{}th : {}, rating: {}, carpark: {}(distance: {}m)".format(idx+1, i['restaurant_name'], i['restaurant_rating'], i['nearest_carpark'], int(i['min_dist'])))