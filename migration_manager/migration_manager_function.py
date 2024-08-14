import functions_framework
import requests
import time
import math
import logging
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed

# TODO: Define in the environment variables
MAX_CONCURRENT_REQUESTS = 10
MAX_CHUNK_SIZE = 10000
THROTTLE_TIME = 0.1

@functions_framework.http
def migration_manager(request):
    """HTTP Cloud Function that splits data into chunks and triggers parallel migrations with error handling."""

    start = time.perf_counter()

    bq_client = bigquery.Client()

    query = """
        SELECT COUNT(*) as total_rows
        FROM `playperfect-432410.game_events.user_panel`
    """
    try:
        query_job = bq_client.query(query)
        total_rows = list(query_job.result())[0]['total_rows']
    except Exception as e:
        logging.error(f"Failed to retrieve total rows from BigQuery: {str(e)}")
        return f"Failed to retrieve total rows from BigQuery: {str(e)}", 500

    chunk_size = MAX_CHUNK_SIZE
    num_chunks = math.ceil(total_rows / chunk_size)

    migrate_chunk_url = "https://us-central1-playperfect-432410.cloudfunctions.net/migrate_chunk"
    errors = []

    def send_chunk_request(chunk_index):
        start_row = chunk_index * chunk_size
        try:
            response = requests.post(migrate_chunk_url, json={
                'start_row': start_row,
                'chunk_size': chunk_size
            })
            if response.status_code != 200:
                return {
                    "chunk_index": chunk_index,
                    "start_row": start_row,
                    "error": response.text
                }
            return None  # No error
        except Exception as e:
            logging.error(f"Failed to trigger migration for chunk {chunk_index + 1}: {str(e)}")
            return {
                "chunk_index": chunk_index,
                "start_row": start_row,
                "error": str(e)
            }

    # Using ThreadPoolExecutor to run requests in parallel
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(send_chunk_request, chunk_index) for chunk_index in range(num_chunks)]
        for future in as_completed(futures):
            error = future.result()
            if error:
                errors.append(error)
            time.sleep(THROTTLE_TIME)  # Throttle requests slightly, might not be necessary

    # Log errors if any occurred
    if errors:
        logging.error(f"Migration encountered errors: {errors}")
        return {
            "message": "Migration completed with errors.",
            "errors": errors
        }, 500

    logging.info(f"Migration completed successfully in {time.perf_counter() - start:.2f} seconds.")
    return 'Migration Manager triggered all chunks successfully.', 200
