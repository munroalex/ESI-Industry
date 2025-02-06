from flask import Flask
from flask_caching import Cache
from app.models import db
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
from app import routes