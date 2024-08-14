import requests

# Define the URL of your Cloud Function
url = "https://us-central1-playperfect-432410.cloudfunctions.net/update_user_panel"

# Make a request to trigger the function
response = requests.get(url)

# Print the response for inspection
print(response.status_code)
print(response.text)
