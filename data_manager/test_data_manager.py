import requests

# To get the bearer token run:
# gcloud auth print-identity-token


def call_cloud_function():
    function_url = (
        "https://us-central1-playperfect-432410.cloudfunctions.net/update_user_panel"
    )

    bearer_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImQyZDQ0NGNmOGM1ZTNhZTgzODZkNjZhMTNhMzE2OTc2YWEzNjk5OTEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIzMjU1NTk0MDU1OS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsImF1ZCI6IjMyNTU1OTQwNTU5LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTAzNDQ4NzIzMTUyMjUyOTY1ODAwIiwiZW1haWwiOiJhY3RhcHBvbkBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6ImdPUE9JbFAzU0dNYlhyNERSRTJoa2ciLCJpYXQiOjE3MjM2OTk4OTgsImV4cCI6MTcyMzcwMzQ5OH0.bWtWaaTbYU_vB-XZrzahbOriC1EgYPrSVScUMldEDzn6mGmHQq0WSHICN3TINRhgOp84DVTJphHJfsWWBvRONFxgOAaXJn4Tx4_AkkJO5rKo69ZZ1PXx4CO1RuXZu5cEdVeT4wZmYhZ1NiJBd4pfU4ZKRWnhiWabW1yMckFF2kiUBxdtl1G4wZBI8mDCHhi9IkjGqzFVBs2k8JwqAAQAJmMmcyQtRRgPOVr2wq-661QWtccKIPBhO968R9ounW0kSrD5rhEg5TVN7FqMGMc9oFDNdoxOX5Lf9cdMAtzHmqA18ehybhLxBHBjE3GFhLQL0ewx0lVTULxOyhP7DFZLrg"
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
