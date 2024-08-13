from fastapi import FastAPI, HTTPException
from google.cloud import bigquery

app = FastAPI()
client = bigquery.Client()


@app.get("/get-user-attribute")
async def get_user_attribute(player_id: str, attribute_name: str):
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

    query = f"""
    SELECT {attribute_name}
    FROM `playperfect-432410.game_events.user_panel`
    WHERE player_id = @player_id
    """

    query_params = [bigquery.ScalarQueryParameter("player_id", "STRING", player_id)]

    job_config = bigquery.QueryJobConfig(query_parameters=query_params)

    try:
        query_job = client.query(query, job_config=job_config)
        result = query_job.result()

        attribute_value = None
        for row in result:
            attribute_value = row.get(attribute_name)

        if attribute_value is None:
            raise HTTPException(
                status_code=404,
                detail=f"Attribute '{attribute_name}' not found for player_id '{player_id}'",
            )

        return {attribute_name: attribute_value}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
