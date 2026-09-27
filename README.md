# Rubber Duck Lending Library

A small Flask prototype for staff to see which members currently hold ducks that are due back in 3 days.

## Features

- Shows all relevant members on one page.
- Shows the total number of ducks each member holds.
- Groups multiple loans of the same duck together.
- Uses Flask + SQLAlchemy.
- Uses an SQLite in-memory database.
- Seeds demo data automatically when the application starts.
- No authentication, external services, or APIs.

## Run

Requires Python 3.10+.

```bash
pip install -r requirements.txt
python app.py
```

Then open:

http://127.0.0.1:5000

Because the database is in memory, the demo data is recreated each time the application starts.
