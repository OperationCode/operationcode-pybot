#!/bin/sh -ex

# Refresh AWS ECR login
AWS_REGION=${AWS_REGION:-us-east-2}
echo "Refreshing AWS ECR login for region ${AWS_REGION}..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin 633607774026.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build and push ARM64 image using buildx with provenance disabled
docker buildx build \
  --platform linux/arm64 \
  --file docker/Dockerfile \
  --tag 633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot:arm64 \
  --provenance=false \
  --push .

# Build and push AMD64 image using buildx with provenance disabled
docker buildx build \
  --platform linux/amd64 \
  --file docker/Dockerfile \
  --tag 633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot:amd64 \
  --provenance=false \
  --push .

# Remove existing manifest list if it exists
docker manifest rm 633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot || true

# Create manifest list
docker manifest create \
  633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot \
  633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot:amd64 \
  633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot:arm64

docker manifest inspect 633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot

# Push the manifest
docker manifest push 633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot
