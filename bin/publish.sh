#!/usr/bin/env bash

# Publishes the most recent web container to docker hubs repo.
# This script assumes docker push works.
# You must set up docker push on your own.

set -eu
IMAGE_ID=$(docker images $IMAGE_NAME:latest --format "{{.ID}}")

if [[ -n "$DOCKER_USERNAME" ]]; then
    echo "Found username";
fi
if [[ -n "$DOCKER_PASSWORD" ]]; then
    echo "Found password";
fi

if [[ -n "$DOCKER_USERNAME" ]] && [[ -n "$DOCKER_PASSWORD" ]]; then
    echo "Logging in using ENV creds"
    echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
fi

echo "Pushing image $IMAGE_NAME:$TRAVIS_BRANCH"
docker tag ${IMAGE_ID} ${DOCKER_REPO}:${TRAVIS_BRANCH}
docker push ${DOCKER_REPO}:${TRAVIS_BRANCH}
