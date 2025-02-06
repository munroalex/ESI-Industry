"""
Module Docstring: This module fetches market data from the ESI API and stores it in a database.
"""
import logging
from flask import Flask
from flask_caching import Cache
from models import db
from fetch_data import fetch_market_orders, fetch_market_history, calculate_daily_sales_volumes

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("main.log"),
        logging.StreamHandler()
    ]
)

### Create the Flask app
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eve_industry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure caching
app.config['CACHE_TYPE'] = 'FileSystemCache' # Store cache files in the filesystem
app.config['CACHE_DEFAULT_TIMEOUT'] = 86400  # 24 hours in seconds
app.config['CACHE_DIR'] = 'cache'  # Directory to store cache files
cache = Cache(app)

# Initialize the database
db.init_app(app)

# Create the tables if they do not exist already
with app.app_context():
    db.create_all()  

### Routes
# Basic Home Route
@app.route("/")
def home() -> str:
    """Basic home route."""
    return "Welcome to the EVE Industry Assistant!"

# Route to fetch market orders
@app.route("/fetch_orders")
@cache.cached(timeout=300)
def fetch_orders() -> str:
    """Fetches market orders for T2 ships and materials in The Forge."""
    id_list: list[str] = []
    with open("t2_ships.txt", "r", encoding="utf-8") as f:
        t2_ships: list[str] = f.readlines()
    for line in t2_ships:
        type_id, _ = line.strip().split(", ")
        id_list.append(type_id)
    with open("t2_materials.txt", "r", encoding="utf-8") as f:
        t2_materials: list[str] = f.readlines()
    for line in t2_materials:
        type_id: str = line.strip().split(", ")
        id_list.append(type_id)
    fetch_market_orders(region_id=10000002, type_ids=id_list)

    return "Market orders fetched and stored!"

# Route to fetch market history
@app.route("/fetch_history")
@cache.cached(timeout=86400)
def fetch_history() -> str:
    """Fetches market history for T2 ships and materials in The Forge."""
    id_list: list[str] = []
    with open("t2_ships.txt", "r", encoding="utf-8") as f:
        t2_ships: list[str] = f.readlines()
    for line in t2_ships:
        type_id, _ = line.strip().split(", ")
        id_list.append(type_id)
    with open("t2_materials.txt", "r", encoding="utf-8") as f:
        t2_materials: list[str] = f.readlines()
    for line in t2_materials:
        type_id: str = line.strip().split(", ")
        id_list.append(type_id)
    fetch_market_history(region_id=10000002, type_ids=id_list)
    for type_id in id_list:
        calculate_daily_sales_volumes(type_id, 10000002)
    return "Market history fetched and stored!"

# Route to analyse market history
@app.route("/analyse")
def analyse() -> str:
    """Analyse the market history for T2 ships in The Forge"""
    ship_list: list[str] = []
    with open("t2_ships.txt", "r", encoding="utf-8") as f:
        t2_ships: list[str] = f.readlines()
    for line in t2_ships:
        type_id, _ = line.strip().split(", ")
        ship_list.append(type_id)
    for type_id in ship_list:
        calculate_daily_sales_volumes(type_id, 10000002)
    return "Market history analysed!"

# Route to clear the cache
@app.route("/clear_cache")
def clear_cache() -> str:
    """Clears the cache."""
    cache.clear()
    return "Cache cleared!"

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
