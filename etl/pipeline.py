"""Run the YouTube ETL pipeline."""

from etl.extract import extract_youtube_data
from etl.load import load_youtube_data
from etl.transform import transform_youtube_data


def run_pipeline():
    """Execute extract, transform, and load steps."""
    raw_data = extract_youtube_data()
    transformed_data = transform_youtube_data(raw_data)
    load_youtube_data(transformed_data)


if __name__ == "__main__":
    run_pipeline()
