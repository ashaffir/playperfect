import logging
import time
from google.cloud import spanner
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

spanner_client = spanner.Client()
instance_id = "players"
database_id = "players_cloned_db"
instance = spanner_client.instance(instance_id)
database = instance.database(database_id)


@app.get("/get-user-attribute/")
async def get_user_attribute(
    player_id: str = Query(..., description="Player ID to fetch the attribute for"),
    attribute_name: str = Query(..., description="Attribute name to fetch"),
):

    start = time.perf_counter()

    logging.info("Received request to get user attribute...")

    # Validate the attribute name to prevent SQL injection
    valid_attributes = [
        "country",
        "avg_price_10",
        "last_weighted_daily_matches_count_10_played_days",
        "active_days_since_last_purchase",
        "score_perc_50_last_5_days",
    ]

    if attribute_name not in valid_attributes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attribute_name '{attribute_name}'. Valid attributes are {valid_attributes}",
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
            raise HTTPException(status_code=404, detail="Player ID not found")

        attribute_value = result_list[0][
            0
        ]  # Access the first column of the first result

        if attribute_value is None:
            raise HTTPException(
                status_code=404,
                detail=f"Attribute '{attribute_name}' not found for player_id '{player_id}'",
            )

    logging.info(f"Time inside app: {time.perf_counter() - start:.2f} seconds")

    return {attribute_name: attribute_value}
