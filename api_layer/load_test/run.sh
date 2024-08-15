#!/bin/sh
uvicorn get_user_attribute_spanner:app --host 0.0.0.0 --port 8080