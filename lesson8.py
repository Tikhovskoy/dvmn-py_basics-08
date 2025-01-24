import json
import requests
from geopy.distance import geodesic
import folium
from decouple import config


DEFAULT_FILE_NAME = "coffee_map.html"
COFFEE_FILE_PATH = "coffee.json"


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def load_coffee_shops(file_path):
    with open(file_path, "r") as coffee_file:
        return json.load(coffee_file)


def calculate_distances(user_coords, coffee_data):
    coffee_shops = []
    for shop in coffee_data:
        name = shop["Name"]
        latitude = float(shop["geoData"]["coordinates"][1])
        longitude = float(shop["geoData"]["coordinates"][0])
        distance = geodesic(user_coords, (latitude, longitude)).kilometers

        coffee_shops.append({
            "title": name,
            "distance": distance,
            "latitude": latitude,
            "longitude": longitude,
        })
    return sorted(coffee_shops, key=lambda x: x["distance"])


def create_map(user_coords, coffee_shops, file_name=DEFAULT_FILE_NAME):
    map_ = folium.Map(location=user_coords, zoom_start=13)

    folium.Marker(
        location=user_coords,
        popup="Вы здесь",
        icon=folium.Icon(color="red"),
    ).add_to(map_)

    for shop in coffee_shops[:5]:
        folium.Marker(
            location=(shop["latitude"], shop["longitude"]),
            popup=f"{shop['title']} ({shop['distance']:.2f} км)",
            icon=folium.Icon(color="blue"),
        ).add_to(map_)

    map_.save(file_name)

def main():
    apikey = config("YANDEX_API_KEY")
    address = input("Где вы находитесь? ").strip()
    user_coords = fetch_coordinates(apikey, address)
    coffee_data = load_coffee_shops(COFFEE_FILE_PATH)
    coffee_shops = calculate_distances(user_coords, coffee_data)
    create_map(user_coords, coffee_shops)


if __name__ == "__main__":
    main()
