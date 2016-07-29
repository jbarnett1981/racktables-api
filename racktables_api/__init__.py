# Imports
import json
from flask import Flask, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from racktables_api.hosts.views import mod as apiv1

# Define the WSGI application object
app = Flask(__name__)
auth = HTTPBasicAuth()

# top level HTTP 404 Error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.', 'status': '404'}), 404)

# Import a module / component using its blueprint handler variable
app.register_blueprint(apiv1)