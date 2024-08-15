import requests

url = "http://34.121.66.186:8080/get-user-attribute/?player_id=6671adc2dd588a8bda035ff4&attribute_name=country"
response = requests.get(url)
data = response.json()
print(data)
