#!/bin/bash

PROJECT_ID=aeroloadinspector
SERVICE_NAME=aeroload
REGION=asia-southeast1
IMAGE=gcr.io/aeroloadinspector/aeroload

echo "🚀 Building image..."
docker build -t $IMAGE .

echo "📤 Pushing image..."
docker push $IMAGE

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --allow-unauthenticated

echo "Running migrations..."
gcloud run jobs execute migrate-job --region $REGION

echo "Done!"

echo "🗄️ Updating migration job..."
gcloud run jobs update migrate-job \
  --image $IMAGE \
  --region $REGION || \
gcloud run jobs create migrate-job \
  --image $IMAGE \
  --region $REGION \
  --command python \
  --args manage.py,migrate

echo "🗄️ Running migrations..."
gcloud run jobs execute migrate-job --region $REGION