# Import flask dependencies
from flask import Blueprint, jsonify, g, request


# Define the blueprint: 'status'
comments = Blueprint('comments', __name__)

@comments.route('/comments', methods=['GET', 'PUT', 'POST', 'DELETE'], strict_slashes=False)
def run_comment(hostname):
    if request.method == 'GET':
        result = g.RacktablesDB.get_comments(hostname)
        return jsonify(result)
