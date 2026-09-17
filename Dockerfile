# Build-only Dockerfile for the sample Flask app.
#
# This image is built by the pipeline's "build" stage to prove the app
# containerizes cleanly. It is NOT pushed to a registry by this
# template — see README.md for how a real deploy stage would extend
# this with `docker push` + a deploy step.

FROM python:3.12-slim AS base

WORKDIR /srv/app

# Install dependencies first so Docker can cache this layer
# independently of application code changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a non-root user for defense in depth.
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000

# gunicorn is not in requirements.txt (dev server is fine for this
# sample); a production image would add gunicorn and run:
#   CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.main:app"]
CMD ["python", "-m", "flask", "--app", "app.main", "run", "--host=0.0.0.0", "--port=8000"]
