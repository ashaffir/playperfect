import requests

# To get the bearer token run:
# gcloud auth print-identity-token


def call_cloud_function():
    function_url = (
        "https://us-central1-playperfect-432410.cloudfunctions.net/update_user_panel"
    )

    bearer_token = "eyJhbGc..."
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # Replace with your actual payload
    payload = {"key": "value"}

    response = requests.post(function_url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")


call_cloud_function()
