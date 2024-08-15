# This script is used to donwload the players' IDs from the spanner, to be used in teh load testing.

from google.cloud import spanner
import csv

spanner_client = spanner.Client()
instance_id = "players"
database_id = "players_cloned_db"

instance = spanner_client.instance(instance_id)
database = instance.database(database_id)

query = "SELECT player_id FROM user_panel"

with database.snapshot() as snapshot:
    results = snapshot.execute_sql(query)

    with open("player_ids.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["player_id"])
        for row in results:
            writer.writerow(row)

print("Export completed.")
