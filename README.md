# Setup on FastAPI app on GCP Cloud RUN 

1. Create exports

```console
export PROJECT_ID=progetti-poc
export APP=rio-fastapi-sns 
export PORT=3000
export REGION=europe-west8
export BRANCH=master
export TAG=${REGION}-docker.pkg.dev/${PROJECT_ID}/${APP}/${APP}:${BRANCH}
```

2. Create Artifact Repo

```console
gcloud artifacts repositories create ${APP} --repository-format Docker --location europe-west8 --project progetti-poc
```

3. Create Build

```console
gcloud builds submit --tag  ${TAG} --project progetti-poc
```

Or

```console
docker build -t ${TAG} .
docker push ${TAG}
```

4. Deploy 

```console
gcloud run deploy $APP --image $TAG --platform managed --region $REGION --port $PORT --allow-unauthenticated --env-vars-file=.env.gcloud
```

5. Clean 

```console
gcloud run services delete $APP --region $REGION 
gcloud run services list
```

# Setup of Infrastructure

1. Comment the `aws_sns_topic_subscription` from the `sns.tf` file

2. Get the app url from GCP 

3. Set the `backend_endpoint` variable in `infrastructure\sns.tf` according to CLoud Run endpoint. This will be used by the SNS subscription to confirm itself.

4. Apply with `terraform apply`

5. Update GCP app environment variables:
    - AWS_S3_BUCKET_NAME 
    - SNS_ENDPOINT_SUBSCRIBE 
    - SNS_TOPIC (arn)

   and re-deploy the app.

6. Enable `aws_sns_topic_subscription` and `terraform apply` again.

# References

* [python-sns-publish-listen](https://github.com/dstilesr/python-sns-publish-listen/tree/master)