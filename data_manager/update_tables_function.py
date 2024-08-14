import functions_framework
import logging
import requests
from google.cloud import bigquery


@functions_framework.http
def update_tables(request):
    """ Update the tables in BigQuery with new data from GCS."""
    logging.info("Start updating the tables.")
    client = bigquery.Client()
    client = bigquery.Client(project="playperfect-432410")

    # Step 1: Load new data from GCS into a temporary table (new_raw_events)
    gcs_uri = "gs://game-events-bucket/players_data_*.parquet"
    new_raw_events_table = "playperfect-432410.game_events.new_raw_events"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    load_job = client.load_table_from_uri(
        gcs_uri, new_raw_events_table, job_config=job_config
    )
    load_job.result()  # Wait for the job to complete

    logging.info(f"Loaded new data into {new_raw_events_table}")

    # Step 2: Append new data to raw_events
    raw_events_sql = """
    INSERT INTO `playperfect-432410.game_events.raw_events`
    SELECT * FROM `playperfect-432410.game_events.new_raw_events`
    """

    query_job = client.query(raw_events_sql)
    query_job.result()  # Wait for the job to complete

    logging.info("Appended new data to raw_events")

    # Step 3: Update user_panel table
    user_panel_sql = """
    CREATE OR REPLACE TABLE `playperfect-432410.game_events.user_panel`
    AS
    WITH raw_data AS (
        SELECT
            player_id,
            timestamp_utc,
            country,
            deposit_amount,
            tournament_score
        FROM
            `playperfect-432410.game_events.raw_events`
    ),
    last_country AS (
        SELECT
            player_id,
            country,
            ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY timestamp_utc DESC) as row_num
        FROM
            raw_data
        WHERE
            country IS NOT NULL
    ),
    avg_price_10 AS (
        SELECT
            player_id,
            AVG(deposit_amount) AS avg_price_10
        FROM (
            SELECT
                player_id,
                deposit_amount,
                ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY timestamp_utc DESC) as row_num
            FROM
                raw_data
            WHERE
                deposit_amount IS NOT NULL
        )
        WHERE
            row_num <= 10
        GROUP BY
            player_id
    ),
    weighted_daily_matches AS (
        SELECT
            player_id,
            SUM(matches_count * weight) / SUM(weight) AS last_weighted_daily_matches_count_10_played_days
        FROM (
            SELECT
                player_id,
                COUNT(*) AS matches_count,
                DENSE_RANK() OVER (PARTITION BY player_id ORDER BY event_date DESC) AS day_rank,
                ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY event_date DESC) AS day_row_num,
                11 - DENSE_RANK() OVER (PARTITION BY player_id ORDER BY event_date DESC) AS weight
            FROM (
                SELECT
                    player_id,
                    DATE(timestamp_utc) AS event_date
                FROM
                    raw_data
                WHERE
                    tournament_score IS NOT NULL
            ) AS sub_query1
            GROUP BY
                player_id,
                event_date
        ) AS sub_query2
        WHERE
            day_rank <= 10
        GROUP BY
            player_id
    ),
    active_days_since_last_purchase AS (
        SELECT
            player_id,
            COUNT(DISTINCT DATE(timestamp_utc)) - 1 AS active_days_since_last_purchase
        FROM
            raw_data
        WHERE
            timestamp_utc > (
                SELECT
                    MAX(timestamp_utc)
                FROM
                    raw_data
                WHERE
                    deposit_amount IS NOT NULL
                    AND raw_data.player_id = player_id
            )
        GROUP BY
            player_id
    ),
    score_perc_50_last_5_days AS (
        SELECT
            player_id,
            APPROX_QUANTILES(tournament_score, 2)[OFFSET(1)] AS score_perc_50_last_5_days
        FROM (
            SELECT
                player_id,
                tournament_score,
                DENSE_RANK() OVER (PARTITION BY player_id ORDER BY DATE(timestamp_utc) DESC) AS day_rank
            FROM
                raw_data
            WHERE
                tournament_score IS NOT NULL
        )
        WHERE
            day_rank <= 5
        GROUP BY
            player_id
    )
    SELECT
        lc.player_id,
        lc.country,
        ap.avg_price_10,
        wdm.last_weighted_daily_matches_count_10_played_days,
        adslp.active_days_since_last_purchase,
        sp.score_perc_50_last_5_days
    FROM
        last_country lc
    LEFT JOIN
        avg_price_10 ap ON lc.player_id = ap.player_id
    LEFT JOIN
        weighted_daily_matches wdm ON lc.player_id = wdm.player_id
    LEFT JOIN
        active_days_since_last_purchase adslp ON lc.player_id = adslp.player_id
    LEFT JOIN
        score_perc_50_last_5_days sp ON lc.player_id = sp.player_id
    GROUP BY
        lc.player_id,
        lc.country,
        ap.avg_price_10,
        wdm.last_weighted_daily_matches_count_10_played_days,
        adslp.active_days_since_last_purchase,
        sp.score_perc_50_last_5_days;
    """

    query_job = client.query(user_panel_sql)
    query_job.result()  # Wait for the job to complete

    # Trigger the migration manager
    try:
        migration_manager_url = 'https://us-central1-playperfect-432410.cloudfunctions.net/migration_manager'
        response = requests.post(migration_manager_url, json={})
        if response.status_code == 200:
            logging.info('Migration Manager triggered successfully.')
        else:
            logging.error(f'Failed to trigger Migration Manager: {response.text}')
            return f'Failed to trigger Migration Manager: {response.text}', 500
    except Exception as e:
        logging.error(f'Error triggering Migration Manager: {str(e)}')
        return f'Error triggering Migration Manager: {str(e)}', 500

    return 'BigQuery table updated and Migration Manager triggered successfully.', 200