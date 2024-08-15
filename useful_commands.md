# Useful GCloud Commands
* Setup / Auth
gcloud auth login
gcloud config set project playperfect-432410
gcloud auth application-default set-quota-project
gcloud init
gcloud app deploy
gcloud login
gcloud auth print-identity-token
gcloud auth print-access-token
gcloud auth list
gcloud auth application-default print-access-token


* Add invocation permissions to all users
gcloud functions add-iam-policy-binding get_player_attribute \
    --region="us-central1" \
    --member="allUsers" \
    --role="roles/cloudfunctions.invoker"


* Add IAM Policy to email account

gcloud projects add-iam-policy-binding playperfect-432410 \
    --member="user:actappon@gmail.com" \
    --role="roles/cloudfunctions.invoker"

* Add IAM Policy to service account
gcloud functions add-iam-policy-binding migrate_chunk \
    --member="serviceAccount:<service-account>@<project-id>.iam.gserviceaccount.com" \
    --role="roles/cloudfunctions.invoker"

gcloud functions add-invoker-policy-binding migration_manager \
      --region="us-central1" \
      --member="serviceAccount:182487233470-compute@developer.gserviceaccount.com"

* Invoke function directly

gcloud functions call migration_manager --data '{}' \
    --project="playperfect-432410" --region="us-central1"

gcloud functions call migrate_chunk --data '{"start_row":0,"chunk_size":10000}' \
    --project="playperfect-432410" --region="us-central1"

* Logs
gcloud functions logs read migrate_chunk --region=us-central1 --limit 10
gcloud functions logs read migration_manager --region=us-central1 

* Spanner
gcloud spanner databases execute-sql players_cloned_db \
    --instance="players" \
    --sql="SELECT COUNT(*) AS total_rows FROM user_panel"
