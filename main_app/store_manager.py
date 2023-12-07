import os
import requests
import googlemaps
import geocoder

class StoreManager():
    def __init__(self):
        self.search_endpoint_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.find_endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        self.details_endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        self.photo_endpoint_url = "https://maps.googleapis.com/maps/api/place/photo"
        self.gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_API_KEY"))

    def get_exact_name(self, store_name):
        search_params = {
            'input': store_name,
            'inputtype': 'textquery',
            'fields': 'name',
            'key': os.environ.get("GOOGLE_API_KEY")
        }

        response = requests.get(self.find_endpoint_url, params=search_params)

        if response.status_code == 200:
            results = response.json().get('candidates', [])
            if not results:
                return "No results found"
            return [(place['name']) for place in results]
        else:
            return f"Error: {response.status_code}"
    
    def get_store_number(self, place_id):
        params = {
            'place_id': place_id,
            'fields': 'name,rating,formatted_phone_number',
            'key': os.environ.get("GOOGLE_API_KEY")
        }

        response = requests.get(self.details_endpoint_url, params=params)

        if response.status_code == 200:
            data = response.json()
            store_number = data['result'].get('formatted_phone_number')
            return store_number
        else:
            print("Error:", response.status_code)
            return None
        
    def get_phone_number(self, place_name):
        places_result = self.gmaps.places(place_name)

        if places_result['status'] == 'OK':
            place_id = places_result['results'][0]['place_id']
            place_details = self.gmaps.place(place_id)
            return place_details['result'].get('formatted_phone_number')
        return "No results found"

    def get_place_id(self, store_name):
        search_params = {
            'input': store_name,
            'inputtype': 'textquery',
            'fields': 'place_id,name',
            'key': os.environ.get("GOOGLE_API_KEY")
        }

        response = requests.get(self.find_endpoint_url, params=search_params)
        
        if response.status_code == 200:
            results = response.json().get('candidates', [])
            if not results:
                return "No results found"
            return [(place['place_id']) for place in results]
        else:
            return f"Error: {response.status_code}"
        
    def get_store_address_by_name(self, store_name):
        place_id = self.get_place_id(store_name)

        if not place_id:
            return "店舗が見つかりません"

        params = {
            'place_id': place_id,
            'fields': 'formatted_address',
            'key': os.environ.get("GOOGLE_API_KEY"),
            'language': 'ja'
        }

        response = requests.get(self.details_endpoint_url, params=params)

        if response.status_code == 200:
            data = response.json().get('result', {})
            return data.get('formatted_address', "住所が見つかりません")
        else:
            return f"エラー: {response.status_code}"
        
    
    def get_store_hours_by_name(self, store_name):
        place_id = self.get_place_id(store_name)
        if not place_id:
            return "店舗が見つかりません"

        params = {
            'place_id': place_id,
            'fields': 'opening_hours',
            'key': os.environ.get("GOOGLE_API_KEY"),
            'language': 'ja'
        }

        response = requests.get(self.details_endpoint_url, params=params)
        if response.status_code == 200:
            data = response.json().get('result', {})
            return data.get('opening_hours', "営業時間情報が見つかりません")
        else:
            return f"エラー: {response.status_code}"
        
    def get_business_status(self, store_name):
        place_id = self.get_place_id(store_name)

        if not place_id:
            return "店舗が見つかりません"

        params = {
            'place_id': place_id,
            'fields': 'business_status',
            'key': os.environ.get("GOOGLE_API_KEY"),
            'language': 'ja'
        }

        response = requests.get(self.details_endpoint_url, params=params)
        if response.status_code == 200:
            data = response.json().get('result', {})
            return data.get('business_status', "ビジネスステータスが見つかりません")
        else:
            return f"エラー: {response.status_code}"
        
    def get_store_info(self, place_id):
        params = {
            'place_id': place_id,
            'fields': 'formatted_address,formatted_phone_number,name,opening_hours,photos,rating,types,url',
            'key': os.environ.get("GOOGLE_API_KEY"),
            'language': 'ja'
        }

        response = requests.get(self.details_endpoint_url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data['result']
        else:
            print("Error:", response.status_code)
            return None
        
    def get_store_photo(self, photo_reference):
        params = {
            'maxwidth':400,
            'photoreference': photo_reference,
            'key': os.environ.get("GOOGLE_API_KEY")
        }

        response = requests.get(self.photo_endpoint_url, params=params)

        if response.status_code == 200:
            return response.content
        else:
            print("Error:", response.status_code)
            return None
    
    def get_store_photo_url(self, photo_reference):
        maxwidth = 400
        return self.photo_endpoint_url + f"?maxwidth={maxwidth}&photoreference={photo_reference}&key={os.environ.get('GOOGLE_API_KEY')}"
        
    def search_store(self, keyword):
        location = geocoder.ip('me').latlng
        search_response = self.gmaps.places_nearby(location=location, keyword=keyword, radius=50000, language="ja")
        stores_info = []
        
        for place in search_response['results']:
            detail_response = self.get_store_info(place["place_id"])
            try:
                store_info = {
                    "place_id": place["place_id"],
                    "name": detail_response["name"],
                    "type": detail_response["types"],
                    "open": detail_response["opening_hours"]["weekday_text"],
                    "open_periods": detail_response["opening_hours"]["periods"],
                    "address": detail_response["formatted_address"],
                    "tel_number": detail_response["formatted_phone_number"],
                    "photos": self.get_store_photo_url(detail_response["photos"][0]["photo_reference"]),
                    "rating": detail_response["rating"],
                    "url": detail_response["url"]
                }
                stores_info.append(store_info)

            except Exception as e:
                print(e)
                pass
        
        return stores_info
    
    def get_store_detail(self,place_id):
        detail_response = self.get_store_info(place_id)
        
        store_info = {}

        store_info["place_id"] = place_id
        store_info["name"] = detail_response["name"]
        store_info["type"] = detail_response["types"]
        store_info["open"] = detail_response["opening_hours"]["weekday_text"]
        store_info["open_periods"] = detail_response["opening_hours"]["periods"]
        store_info["address"] = detail_response["formatted_address"]
        store_info["tel_number"] = detail_response["formatted_phone_number"]
        
        store_info["photos"] = [self.get_store_photo_url(detail_response["photos"][0]["photo_reference"])]
        try:
            store_info["photos"].append(self.get_store_photo_url(detail_response["photos"][1]["photo_reference"]))
        except Exception as e:
            pass
        try:
            store_info["photos"].append(self.get_store_photo_url(detail_response["photos"][2]["photo_reference"]))
        except Exception as e:
            pass

        store_info["rating"] = detail_response["rating"]
        store_info["url"] = detail_response["url"]

        return store_info
