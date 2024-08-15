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
![Solution Architecture](./playperfect-architecture.jpg)

### Data Manager
Loading the data from the paruqet files to the BigQuery, and trigger its copy to Google Spanner storage.

### Migration Manager
Handles the migration of the data from BigQuery to the Google Spanner.
* Migration manager receives the trigger from the data manager, splits the data to chunks and runs multiple services in parallel to load it to the spanner.
* Migrate Chunk function receives the information to load to the spanner.

### API Layer
Handles requests from clients.
The implementation of the API layer was initially done with a VM (get_user_attribute_spanner_vm.py), which resulted with poor performance. 
So, I switched to Function, which gave much better results.


## Performance
* The image below is a screenshot of the locust run.
![API Performance](./api-performance.jpg)

* The image below is the function logs
![Inner look](./api-logs.jpg)

#### Notes:
- As you can see, though there are much more than 100 RPS (required), the response time is 350ms on the 95th percentile.
This would be mostly a network latency, rather than the app response which measured which is clearly seen in the logs. 


## To Do
### Operations
* Proper application run
  Currently the API is running from within a Tmux session so that it wont stop then the SSH is closed. 
  This should be modified for production level.

### Unit testing
* Extend the simple tests to a more thorough tests that cover all relevant functionalities of each unit
  
### DevOps/IT
* Security
- Clean up permissions and roles
