# Import flask dependencies
from flask import Blueprint, jsonify, g, request


# Define the blueprint: 'status'
status = Blueprint('status', __name__)

@status.route('/comments', methods=['GET', 'PUT', 'POST', 'DELETE'], strict_slashes=False)
def run1(hostname):
    if request.method == 'GET':
        result = g.RacktablesDB.get_comments(hostname)
        return jsonify(result)
