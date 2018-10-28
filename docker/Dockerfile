FROM python:3.7-slim

# Create and set the working directory to /pybot
WORKDIR /pybot

# Copy the pipfile into the pybot directory
COPY Pipfile* /pybot/

# Install anything missing from the slim image, install dependnecies, remove anything only needed for building
# This is run as one line so docker caches it as a single layer.
RUN apt-get update \
    && apt-get install -y gcc  \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pipenv \
    && pipenv install --system --deploy --dev \
    && apt-get purge -y --auto-remove gcc

# Copy the rest of our app into the container
COPY . /pybot

# Run the pybot module
ENTRYPOINT ["python3", "-m", "pybot"]