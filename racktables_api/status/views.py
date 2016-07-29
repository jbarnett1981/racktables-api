# Import flask dependencies
from flask import Blueprint, jsonify, g, request


# Define the blueprint: 'status'
status = Blueprint('status', __name__)

@status.route('/', methods=['GET'], strict_slashes=False)
def run_status():
    if request.method == 'GET':
        result = g.RacktablesDB.get_comments(hostname)
        return jsonify(result)