import logging
from fastapi import FastAPI, HTTPException, Query
from google.cloud import spanner

app = FastAPI()

spanner_client = spanner.Client()
instance = spanner_client.instance('players')
database = instance.database('players_cloned_db')

@app.get("/get-user-attribute/")
async def get_user_attribute(
    player_id: str = Query(..., description="Player ID to fetch the attribute for"),
    attribute_name: str = Query(..., description="Attribute name to fetch")
):

    logging.info(f"Fetching attribute '{attribute_name}' for player_id '{player_id}' from Spanner...")

    # Validate the attribute name
    valid_attributes = [
        "country", "avg_price_10", "last_weighted_daily_matches_count_10_played_days",
        "active_days_since_last_purchase", "score_perc_50_last_5_days"
    ]

    if attribute_name not in valid_attributes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attribute_name '{attribute_name}'. Valid attributes are {valid_attributes}"
        )

    try:
        # Query Spanner for the requested attribute
        with database.snapshot() as snapshot:
            query = f"""
                SELECT {attribute_name}
                FROM user_panel
                WHERE player_id = @player_id
            """
            results = snapshot.execute_sql(
                query,
                params={"player_id": player_id},
                param_types={"player_id": spanner.param_types.STRING},
            )

            # Fetch the first result (there should be only one result per player_id)
            row = next(results, None)

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Attribute '{attribute_name}' not found for player_id '{player_id}'"
                )

            attribute_value = row[0]
            return {attribute_name: attribute_value}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the attribute: {str(e)}"
        )