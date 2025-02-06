"""
Module Docstring: This module fetches market data from the ESI API and stores it in a database.
"""
# Imports
import logging
from datetime import datetime, timedelta
import os
import pickle

import requests
from sqlalchemy import func

from custom_exceptions import UnexpectedException
from app.models import db, MarketOrder, MarketHistory

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fetch_data.log"),
        logging.StreamHandler()
    ]
)

# Cache to store the last fetch time for each region and type_id
CACHE_FILE = "fetch_cache.pkl"

def load_cache():
    """Load the fetch cache from disk."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_cache(cache):
    """Save the fetch cache to disk."""
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)

fetch_cache = load_cache()

def should_fetch(region_id, type_id, current_time):
    """Check if we should fetch new data based on the last fetch time."""
    cache_key = (region_id, type_id)
    if cache_key in fetch_cache:
        last_fetch_time = fetch_cache[cache_key]
        if (current_time - last_fetch_time).total_seconds() < 300:
            logging.info("Skipping fetch for region_id:"
                         " %s and type_id: %s due to cache.", region_id, type_id)
            return False
    return True

def fetch_orders_from_api(region_id, type_id):
    """Fetch market orders from the ESI API for a specific type ID in a region."""
    url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/"
    params = {
        "type_id": type_id,
        "order_type": "all",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    return response.json()

def process_orders(region_id, orders):
    """Process the fetched orders and store them in the database."""
    new_orders = []
    for order in orders:
        try:
            # Check if the order already exists in the database
            existing_order = MarketOrder.query.filter_by(order_id=order['order_id']).first()
            if not existing_order:
                new_order = MarketOrder(
                    order_id=order['order_id'],
                    type_id=order['type_id'],
                    region_id=region_id,
                    price=order['price'],
                    volume_remain=order['volume_remain'],
                    volume_total=order['volume_total'],
                    is_buy_order=order['is_buy_order'],
                    issued=datetime.strptime(order['issued'], '%Y-%m-%dT%H:%M:%SZ'),
                )
                new_orders.append(new_order)
            else:
                # Update the existing order if any data has changed
                updated = False
                if existing_order.price != order['price']:
                    existing_order.price = order['price']
                    updated = True
                if existing_order.volume_remain != order['volume_remain']:
                    existing_order.volume_remain = order['volume_remain']
                    updated = True
                if existing_order.volume_total != order['volume_total']:
                    existing_order.volume_total = order['volume_total']
                    updated = True
                if existing_order.is_buy_order != order['is_buy_order']:
                    existing_order.is_buy_order = order['is_buy_order']
                    updated = True
                if existing_order.issued != datetime.strptime(
                    order['issued'], '%Y-%m-%dT%H:%M:%SZ'
                    ):
                    existing_order.issued = datetime.strptime(order['issued'], '%Y-%m-%dT%H:%M:%SZ')
                    updated = True
                if updated:
                    db.session.add(existing_order)
        except UnexpectedException as e:
            logging.error("Error processing order %s: %s", order['order_id'], e)
    if new_orders:
        db.session.bulk_save_objects(new_orders)
    db.session.commit()

def fetch_market_orders(region_id, type_ids):
    """
    Fetch market orders for a list of type IDs in a specific region and store them in the database.

    :param region_id: The region ID (e.g., 10000002 for Jita).
    :param type_ids: A list of type IDs (e.g., [1201, 1202] for Kestrel and Condor).
    """
    current_time = datetime.now()
    for type_id in type_ids:
        if not should_fetch(region_id, type_id, current_time):
            continue

        try:
            orders = fetch_orders_from_api(region_id, type_id)
            process_orders(region_id, orders)
            fetch_cache[(region_id, type_id)] = current_time
            save_cache(fetch_cache)
            logging.info("Fetched and stored %s orders for type_id: %s in region_id: %s.",
                         len(orders), type_id, region_id)
        except requests.exceptions.RequestException as e:
            logging.error("Error fetching market orders for type_id %s: %s", type_id, e)
        except UnexpectedException as e:
            logging.error("Unexpected error: %s", e)

def fetch_market_history(region_id, type_ids):
    """
    Fetch historical market data for a list of type IDs in a specific region,
    store it in the database.

    :param region_id: The region ID (e.g., 10000002 for Jita).
    :param type_ids: A list of type IDs (e.g., [1201, 1202] for Kestrel and Condor).
    """
    for type_id in type_ids:
        try:
            # Fetch historical data from the ESI API
            url = f"https://esi.evetech.net/latest/markets/{region_id}/history/"
            params = {
                "type_id": type_id,
            }
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                history_data = response.json()
                for entry in history_data:
                    # Parse the date
                    date = datetime.strptime(entry['date'], '%Y-%m-%d').date()

                    # Check if the entry already exists in the database
                    existing_entry = MarketHistory.query.filter_by(
                        type_id=type_id,
                        region_id=region_id,
                        date=date,
                    ).first()
                    if not existing_entry:
                        # Create a new MarketHistory object
                        new_entry = MarketHistory(
                            type_id=type_id,
                            region_id=region_id,
                            date=date,
                            volume=entry['volume'],
                            average_price=entry['average'],
                        )
                        db.session.add(new_entry)
                db.session.commit()
                logging.info("Fetched and stored historical data for type_id: %s in region_id: %s.",
                             type_id, region_id)
            else:
                logging.error("Error fetching historical data for type_id %s: %s - %s",
                              type_id, response.status_code, response.text)

        except UnexpectedException as e:
            logging.error("An error occurred while processing type_id %s: %s", type_id, e)

def calculate_daily_sales_volumes(type_id, region_id):
    """
    Calculate the last 30 and 60-day daily sales volumes for a specific type ID in a region.

    :param type_id: The type ID (e.g., 1201 for Kestrel).
    :param region_id: The region ID (e.g., 10000002 for Jita).
    :return: A dictionary with the 30-day and 60-day average daily volumes.
    """
    # Get the current date
    today = datetime.now.date()

    # Calculate the start dates for the last 30 and 60 days
    start_date_30 = today - timedelta(days=30)
    start_date_60 = today - timedelta(days=60)

    # Query the database for the last 30 and 60 days
    volumes_30 = db.session.query(func.sum(MarketHistory.volume)).filter(
        MarketHistory.type_id == type_id,
        MarketHistory.region_id == region_id,
        MarketHistory.date >= start_date_30,
    ).scalar() or 0

    volumes_60 = db.session.query(func.sum(MarketHistory.volume)).filter(
        MarketHistory.type_id == type_id,
        MarketHistory.region_id == region_id,
        MarketHistory.date >= start_date_60,
    ).scalar() or 0

    # Calculate average daily volumes
    avg_daily_volume_30 = volumes_30 / 30
    avg_daily_volume_60 = volumes_60 / 60

    logging.info("Average daily volume for type_id %s{type_id}"
                 " in region_id %s{region_id} (last 30 days): %s{avg_daily_volume_30}",
                 type_id, region_id, avg_daily_volume_30)
    logging.info("Average daily volume for type_id %s{type_id}"
          " in region_id %s{region_id} (last 60 days): %s{avg_daily_volume_60}",
            type_id, region_id, avg_daily_volume_60)
    return None
