# YouTube ETL Pipeline

Project scaffold for extracting YouTube data, transforming it, loading it into a database, and analyzing it in a notebook.

## Structure

```text
etl/
  extract.py
  transform.py
  load.py
  pipeline.py
analysis/
  youtube_analysis.ipynb
logs/
sql/
  create_tables.sql
config.py
requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

Add your YouTube API key and database settings to `config.py`.

## Run

```bash
python -m etl.pipeline
```
