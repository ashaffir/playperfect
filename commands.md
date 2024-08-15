# Useful GCloud Commands

* Add IAM Policy to email account

gcloud projects add-iam-policy-binding playperfect-432410 \
    --member="user:actappon@gmail.com" \
    --role="roles/cloudfunctions.invoker"

* Add IAM Policy to service account
gcloud functions add-iam-policy-binding migrate_chunk \
    --member="serviceAccount:<service-account>@<project-id>.iam.gserviceaccount.com" \
    --role="roles/cloudfunctions.invoker"

* Invoke function directly

gcloud functions call migration_manager --data '{}'

gcloud functions call migrate_chunk --data '{"start_row":0,"chunk_size":10000}' \
    --project="playperfect-432410" --region="us-central1"


