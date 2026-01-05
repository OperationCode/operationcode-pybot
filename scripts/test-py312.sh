#!/bin/bash
# Run tests in Python 3.12 Docker container
set -e

cd "$(dirname "$0")/.."

echo "🐍 Running tests in Python 3.12 container..."
docker build -t pybot-test:py312 -f docker/Dockerfile.test.py312 .
docker run --rm \
    -e SLACK_TOKEN=test_token \
    -e SLACK_VERIFY=supersecuretoken \
    -e SLACK_BOT_USER_ID=bot_user_id \
    -e SLACK_BOT_ID=bot_id \
    -e AIRTABLE_API_KEY=test_key \
    -e AIRTABLE_BASE_KEY=test_base \
    -e YELP_TOKEN=test_yelp \
    -e BACKEND_AUTH_TOKEN=devBackendToken \
    pybot-test:py312 \
    poetry run pytest -v "$@"
