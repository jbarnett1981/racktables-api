# Imports
import json
from flask import Flask, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from racktables_api.main.views import main
from racktables_api.hosts.views import hosts

# Define the WSGI application object
app = Flask(__name__)
auth = HTTPBasicAuth()

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