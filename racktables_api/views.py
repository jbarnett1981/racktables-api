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
mod = Blueprint('api', __name__, url_prefix='/hosts')

# Create database connection session before request if not exist
@mod.before_request
def before_request():
    g.RacktablesDB = RacktablesDB(host, username, password, db)
    g.RacktablesDB.connect()

# Close database connection session if not already closed
@mod.teardown_request
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

@mod.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'message': 'The request contained invalid data. Please try again.', 'status': '400'}), 400)

@mod.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.', 'status': '404'}), 404)

@mod.errorhandler(409)
def bad_request(error):
    return make_response(jsonify({'message': 'A resource with that name or ID already exists.', 'status': '409'}), 409)


@mod.errorhandler(410)
def not_found(error):
    return make_response(jsonify({'message': 'A resource with that name cannot be found.', 'status': '410'}), 410)

@mod.route('/', methods=['GET'], strict_slashes=False)
def get():
    RacktablesDB = get_db()
    result = RacktablesDB.get_all_objects()
    return jsonify(result)

@mod.route('/<string:hostname>', methods=['GET', 'PUT', 'POST', 'DELETE'], strict_slashes=False)
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

@mod.route('/<string:hostname>/comments', methods=['GET', 'PUT', 'POST', 'DELETE'])
def run1(hostname):
    RacktablesDB = get_db()
    if request.method == 'GET':
        result = RacktablesDB.get_comments(hostname)
        return jsonify(result)
