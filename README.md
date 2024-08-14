# PlayPerfect Home Assignment
## GCP Resources
- Project ID: playperfect-432410
- [IAM and Admin](https://console.cloud.google.com/iam-admin/iam?referrer=search&hl=en&project=playperfect-432410)
- [Project Admin](https://console.cloud.google.com/welcome/new?project=playperfect-432410&hl=en)
- [BigQuery API](https://console.cloud.google.com/apis/api/bigquery.googleapis.com/metrics?hl=en&project=playperfect-432410)
  - Client ID: 182487233470-e4qcnqhgdmqe80pm6jmhtpb2n7vu86kk.apps.googleusercontent.com
- [Google Storage](https://console.cloud.google.com/storage/browser/game-events-bucket?hl=en&project=playperfect-432410)
- [Google Spanner](https://console.cloud.google.com/spanner/instances?authuser=1&project=playperfect-432410)
- [Cloud Functions](https://console.cloud.google.com/functions/list?referrer=search&hl=en&project=playperfect-432410)
- [Cloud Scheduler](https://console.cloud.google.com/cloudscheduler?referrer=search&hl=en&project=playperfect-432410)
- [Cloud Compute](https://console.cloud.google.com/compute/instances?authuser=1&project=playperfect-432410)

## Architecture
![Solution Architecture](./playperfect-architecture-pipeline.png)

### Data Manager
Loading the data from the paruqet files to the BigQuery, and trigger its copy to Google Spanner storage.

### Migration Manager
Handles the migration of the data from BigQuery to the Google Spanner.
* Migration manager receives the trigger from the data manager, splits the data to chunks and runs multiple services in parallel to load it to the spanner.
* Migrate Chunk function receives the information to load to the spanner.

### API Layer
Handles requests from clients.
This code runs in a VM.
