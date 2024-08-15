import json
import time
import logging
import functions_framework
from google.cloud import spanner

project_id = "playperfect-432410"
instance_id = "players"
database_id = "players_cloned_db"

spanner_client = spanner.Client(project=project_id)
instance = spanner_client.instance(instance_id)
database = instance.database(database_id)


@functions_framework.http
def get_user_attribute(request):

    start = time.perf_counter()

    logging.info("Received request to get user attribute...")

    player_id = request.args.get("player_id")
    attribute_name = request.args.get("attribute_name")

    if not player_id or not attribute_name:
        return (
            json.dumps({"error": "Both player_id and attribute_name are required"}),
            400,
        )

    valid_attributes = [
        "country",
        "avg_price_10",
        "last_weighted_daily_matches_count_10_played_days",
        "active_days_since_last_purchase",
        "score_perc_50_last_5_days",
    ]

    if attribute_name not in valid_attributes:
        return (
            json.dumps(
                {
                    "error": f"Invalid attribute_name '{attribute_name}'. Valid attributes are {valid_attributes}"
                }
            ),
            400,
        )

    query = f"SELECT {attribute_name} FROM user_panel WHERE player_id = @player_id"

    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            query,
            params={"player_id": player_id},
            param_types={"player_id": spanner.param_types.STRING},
        )
        result_list = list(results)

        if not result_list:
            return json.dumps({"error": "Player ID not found"}), 404

        attribute_value = result_list[0][0]

        if attribute_value is None:
            return (
                json.dumps(
                    {
                        "error": f"Attribute '{attribute_name}' not found for player_id '{player_id}'"
                    }
                ),
                404,
            )

    logging.info(f"Time inside app: {time.perf_counter() - start:.2f} seconds")
    print(f"Time inside app: {time.perf_counter() - start:.2f} seconds")

    return json.dumps({attribute_name: attribute_value}), 200
