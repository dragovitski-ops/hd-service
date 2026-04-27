# Human Design API Service

Python FastAPI service for Human Design chart calculation using Swiss Ephemeris.

## Deploy to Railway

1. Push this folder to GitHub
2. Connect Railway to the GitHub repo
3. Railway auto-deploys

## API Usage

POST /calculate
{
  "year": 1978,
  "month": 11,
  "day": 25,
  "hour": 9,
  "minute": 30,
  "utc_offset": 2.0
}
