import random
from locust import FastHttpUser, task

VM_URL = "http://34.121.66.186:8080/get-user-attribute"
FUNCTION_URL = (
    "https://us-central1-playperfect-432410.cloudfunctions.net/get_player_attribute"
)


class StressUser(FastHttpUser):

    @task
    def index(self):
        # Load the players' IDs from CSV
        ids_file = "./player_ids.csv"
        with open(ids_file, "r") as f:
            ids = f.read().splitlines()
            ids = [x for x in ids if x != "player_id"]

        user_id = random.choices(ids)[0]
        api_url = f"{FUNCTION_URL}?player_id={user_id}&attribute_name=country"
        res = self.client.get(api_url)

        print(f"Requested URL {api_url}: {res.content}")
