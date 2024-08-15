from google.cloud import spanner

# Initialize Spanner client and connect to your instance and database
spanner_client = spanner.Client()
instance_id = "players"
database_id = "players_cloned_db"

instance = spanner_client.instance(instance_id)
database = instance.database(database_id)

# Define your query
player_id = "6671adc2dd588a8bda035ff4"
query = "SELECT country FROM user_panel WHERE player_id = @player_id"

with database.snapshot() as snapshot:
    results = snapshot.execute_sql(
        query,
        params={"player_id": player_id},
        param_types={"player_id": spanner.param_types.STRING},
    )
    for row in results:
        print(f"Player Country: {row[0]}")
