# Import flask dependencies
from flask import Blueprint, g

# Define the blueprint: 'api'
main = Blueprint('main', __name__)

@main.route('/', methods=['GET'], strict_slashes=False)
def get():
    return 'Hello, World!'