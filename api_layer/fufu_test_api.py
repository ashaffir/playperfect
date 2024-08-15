import requests
import time

# Testing the VM
print("VM Test")
url = "http://34.121.66.186:8080/get-user-attribute/?player_id=6671adc2dd588a8bda03b92a&attribute_name=country"
start = time.perf_counter()
response = requests.get(url)
data = response.json()
print(f"{data=} | time: {time.perf_counter() - start}")

print(30 * "#")

print("Function Test")
f_url = "https://us-central1-playperfect-432410.cloudfunctions.net/get_player_attribute?player_id=6671adc2dd588a8bda03b92a&attribute_name=country"
f_start = time.perf_counter()
f_response = requests.get(url)
f_data = f_response.json()
print(f"{f_data=} | time: {time.perf_counter() - f_start}")
