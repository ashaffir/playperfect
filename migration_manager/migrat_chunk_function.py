import logging
import functions_framework
from google.cloud import bigquery, spanner
from google.cloud import exceptions

@functions_framework.http
def migrate_chunk(request):
    """HTTP Cloud Function that migrates a chunk of data from BigQuery to Cloud Spanner with error handling."""

    request_json = request.get_json(silent=True)
    start_row = request_json.get('start_row')
    chunk_size = request_json.get('chunk_size')
    logging.info(f"Received request to migrate chunk starting at row {start_row} with size {chunk_size}")

    bq_client = bigquery.Client()

    # Query to get the specific chunk of data
    query = f"""
        SELECT
            player_id,
            country,
            avg_price_10,
            last_weighted_daily_matches_count_10_played_days,
            active_days_since_last_purchase,
            score_perc_50_last_5_days
        FROM `playperfect-432410.game_events.user_panel`
        LIMIT {chunk_size}
        OFFSET {start_row}
    """

    try:
        query_job = bq_client.query(query)
        rows = list(query_job.result())

        if not rows:
            return f'No data found for chunk starting at row {start_row}', 404

    except Exception as e:
        logging.error(f"Failed to retrieve data from BigQuery: {str(e)}")
        return f"Failed to retrieve data from BigQuery: {str(e)}", 500

    # Initialize Spanner client, process and insert data into Spanner
    try:
        spanner_client = spanner.Client()
        instance = spanner_client.instance('players')
        database = instance.database('players_cloned_db')
    except Exception as e:
        logging.error(f"Failed to initialize Spanner client: {str(e)}")
        return f"Failed to initialize Spanner client: {str(e)}", 500

    rows_to_insert = [
        (
            row['player_id'],
            row['country'],
            row['avg_price_10'],
            row['last_weighted_daily_matches_count_10_played_days'],
            row['active_days_since_last_purchase'],
            row['score_perc_50_last_5_days']
        ) for row in rows
    ]

    try:
        with database.batch() as batch:
            batch.insert(
                table='user_panel',
                columns=(
                    'player_id',
                    'country',
                    'avg_price_10',
                    'last_weighted_daily_matches_count_10_played_days',
                    'active_days_since_last_purchase',
                    'score_perc_50_last_5_days'
                ),
                values=rows_to_insert
            )
    except exceptions.GoogleAPICallError as e:
        logging.error(f"Failed to insert data into Spanner: {str(e)}")
        return f"Failed to insert data into Spanner: {str(e)}", 500
    except exceptions.RetryError as e:
        logging.error(f"Retry error during Spanner operation: {str(e)}")
        return f"Retry error during Spanner operation: {str(e)}", 500
    except Exception as e:
        logging.error(f"Unexpected error during Spanner operation: {str(e)}")
        return f"Unexpected error during Spanner operation: {str(e)}", 500

    logging.info(f"Successfully migrated chunk starting at row {start_row}")
    return f'Successfully migrated chunk starting at row {start_row}', 200
