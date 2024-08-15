import random
import time
from locust import FastHttpUser, task

# from cids import user_id, insts, insts_short, cids_short

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
        # time.sleep(1)
        # api_url = f"{VM_URL}?player_id={user_id}&attribute_name=country"
        api_url = f"{FUNCTION_URL}?player_id={user_id}&attribute_name=country"
        res = self.client.get(api_url)

        print(f"Requested URL {api_url}: {res.content}")
