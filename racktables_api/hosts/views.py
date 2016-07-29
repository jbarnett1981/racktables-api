# Import flask dependencies
from flask import Blueprint, jsonify, g, request


# Define the blueprint: 'hosts'
hosts = Blueprint('hosts', __name__)



@hosts.route('/', methods=['GET'], strict_slashes=False)
def get_hosts():
    result = g.RacktablesDB.get_all_objects()
    return jsonify(result)

@hosts.route('/<string:hostname>', methods=['GET', 'PUT', 'POST', 'DELETE'], strict_slashes=False)
def run_host(hostname):
    if request.method == 'GET':

        result = g.RacktablesDB.get(hostname)
        return jsonify(result)

    elif request.method == 'PUT':
        result = g.RacktablesDB.put(hostname, request.form)
        return jsonify(result)

    elif request.method == 'POST':
        result = g.RacktablesDB.post(hostname, request.form)
        return jsonify(result)

    elif request.method == 'DELETE':
        result = g.RacktablesDB.delete(hostname)
        return jsonify(result)

# @hosts.route('/<string:hostname>/comments', methods=['GET', 'PUT', 'POST', 'DELETE'])
# def run1(hostname):
#     if request.method == 'GET':
#         result = g.RacktablesDB.get_comments(hostname)
#         return jsonify(result)
