"""
Module Docstring: This module fetches market data from the ESI API and stores it in a database.
"""
import logging
from flask import Flask
from flask_caching import Cache
from app.models import db
from fetch_data import fetch_market_orders, fetch_market_history, calculate_daily_sales_volumes
from app import app

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("main.log"),
        logging.StreamHandler()
    ]
)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
