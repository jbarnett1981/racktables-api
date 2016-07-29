# Imports
import json
import yaml
from flask import Flask, jsonify, make_response, g
from flask_httpauth import HTTPBasicAuth
from racktables_api.main.views import main
from racktables_api.hosts.views import hosts
from racktables_api.status.views import status
from racktables_api.database import is_number, RacktablesDB

# Get connection details
with open('config/db.yaml', 'r') as f:
    config = yaml.load(f.read())
    host = config['production']['host']
    username = config['production']['username']
    password = config['production']['password']
    db = config['production']['db']

# Connection handling function
def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'RacktablesDB'):
        g.RacktablesDB = RacktablesDB(host, username, password, db)
        g.RacktablesDB.connect()
    return g.RacktablesDB

# Define the WSGI application object
app = Flask(__name__)
auth = HTTPBasicAuth()

# Create database connection session before request if not exist
@app.before_request
def before_request():
    g.RacktablesDB = RacktablesDB(host, username, password, db)
    g.RacktablesDB.connect()

# Close database connection session if not already closed
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'RacktablesDB', None)
    if db is not None:
        db.close()

# Error handling
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'message': 'The request contained invalid data. Please try again.', 'status': '400'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.', 'status': '404'}), 404)

@app.errorhandler(409)
def bad_request(error):
    return make_response(jsonify({'message': 'A resource with that name or ID already exists.', 'status': '409'}), 409)

@app.errorhandler(410)
def not_found(error):
    return make_response(jsonify({'message': 'A resource with that name cannot be found.', 'status': '410'}), 410)


# Import a module / component using its blueprint handler variable
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(hosts, url_prefix='/hosts')
app.register_blueprint(status, url_prefix='/hosts/<string:hostname>')