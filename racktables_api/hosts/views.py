# Import flask dependencies
from flask import Blueprint, jsonify, g, request, make_response, abort

# Import yaml for db config file parsing
import yaml

# Import database class
from racktables_api.database import is_number, RacktablesDB

# Get connection details
with open('config/db.yaml', 'r') as f:
    config = yaml.load(f.read())
    host = config['production']['host']
    username = config['production']['username']
    password = config['production']['password']
    db = config['production']['db']

# Define the blueprint: 'api'
hosts = Blueprint('hosts', __name__)

# Create database connection session before request if not exist
@hosts.before_request
def before_request():
    g.RacktablesDB = RacktablesDB(host, username, password, db)
    g.RacktablesDB.connect()

# Close database connection session if not already closed
@hosts.teardown_request
def teardown_request(exception):
    db = getattr(g, 'RacktablesDB', None)
    if db is not None:
        db.close()

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

@hosts.route('/', methods=['GET'], strict_slashes=False)
def get():
    RacktablesDB = get_db()
    result = RacktablesDB.get_all_objects()
    return jsonify(result)

@hosts.route('/<string:hostname>', methods=['GET', 'PUT', 'POST', 'DELETE'], strict_slashes=False)
def run(hostname):
    RacktablesDB = get_db()
    if request.method == 'GET':

        result = RacktablesDB.get(hostname)
        return jsonify(result)

    elif request.method == 'PUT':
        result = RacktablesDB.put(hostname, request.form)
        return jsonify(result)

    elif request.method == 'POST':
        result = RacktablesDB.post(hostname, request.form)
        return jsonify(result)

    elif request.method == 'DELETE':
        result = RacktablesDB.delete(hostname)
        return jsonify(result)

@hosts.route('/<string:hostname>/comments', methods=['GET', 'PUT', 'POST', 'DELETE'])
def run1(hostname):
    RacktablesDB = get_db()
    if request.method == 'GET':
        result = RacktablesDB.get_comments(hostname)
        return jsonify(result)
