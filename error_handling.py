'''
jbarnett
7/22/2016

error handling classes and vars for racktables api
'''

from flask_restful import HTTPException

class BadRequest(HTTPException):
    code = 400

class ResourceAlreadyExists(HTTPException):
    code = 409

class ResourceDoesNotExist(HTTPException):
    code = 410


errors = {
    'ResourceAlreadyExists': {
        'message': "A resource with that name or ID already exists.",
        'status': 409,
    },
    'ResourceDoesNotExist': {
        'message': "A resource with that name or ID no longer exists.",
        'status': 410,
    },
    'NotFound': {
        'message': "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.",
        'status': 404,
    },
    'BadRequest': {
        'message': "The request contained invalid data. Please try again.",
        'status': 400,
    },
}