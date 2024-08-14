import random
import time
from locust import FastHttpUser, task
# from cids import user_id, insts, insts_short, cids_short

function_url = "http://34.121.66.186:8080/get-user-attribute?player_id=6671adc3dd588a8bda04cff0&attribute_name=country"
localhost_url = "http://localhost:7071"

class StressUser(FastHttpUser):
    @task
    def index(self):
        # cid = random.choices(cids)[0]
        # instrument = random.choices(insts)[0]
        # time.sleep(1)
        res = self.client.get(function_url)
        # res = self.client.get(f"/{cid}")
        # res = self.client.get(f"/api/recommedations/m1/{cid}")

        print(res.url)
        print(res.content)
