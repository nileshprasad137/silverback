"""
Register API Endpoint
"""

import json

# Django
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext as _

# local Django
from app.modules.validation.form import Form
from app.modules.util.helpers import Helpers
from app.modules.core.request import Request
from app.modules.core.response import Response
from app.modules.core.user import User as User_Module
from app.modules.core.decorators import stop_request_if_authenticated


class Register(View):

    __request = None
    __response = None
    __helpers = None
    __form = None
    __user = None
    __logger = None

    def __init__(self):
        self.__request = Request()
        self.__response = Response()
        self.__helpers = Helpers()
        self.__form = Form()
        self.__user = User_Module()
        self.__logger = self.__helpers.get_logger(__name__)

    @stop_request_if_authenticated
    def post(self, request):

        self.__request.set_request(request)

        request_data = self.__request.get_request_data("post", {
            "register_request_token": "",
            "first_name": "",
            "last_name": "",
            "username": "",
            "email": "",
            "password": ""
        })

        self.__form.add_inputs({
            'first_name': {
                'value': request_data["first_name"],
                'sanitize': {
                    'strip': {}
                },
                'validate': {
                    'names': {
                        'error': _('Error! First name contains invalid characters.')
                    },
                    'length_between': {
                        'param': [0, 20],
                        'error': _('Error! First name must be 1 to 20 characters long.')
                    }
                }
            },
            'last_name': {
                'value': request_data["last_name"],
                'sanitize': {
                    'strip': {}
                },
                'validate': {
                    'names': {
                        'error': _('Error! Last name contains invalid characters.')
                    },
                    'length_between': {
                        'param': [0, 20],
                        'error': _('Error! Last name must be 1 to 20 characters long.')
                    }
                }
            },
            'username': {
                'value': request_data["username"],
                'sanitize': {
                    'escape': {},
                    'strip': {}
                },
                'validate': {
                    'alpha_numeric': {
                        'error': _('Error! Username must be alpha numeric.')
                    },
                    'length_between': {
                        'param': [4, 10],
                        'error': _('Error! Username must be 5 to 10 characters long.')
                    }
                }
            },
            'email': {
                'value': request_data["email"],
                'sanitize': {
                    'escape': {},
                    'strip': {}
                },
                'validate': {
                    'email': {
                        'error': _('Error! Admin email is invalid.')
                    }
                }
            },
            'password': {
                'value': request_data["password"],
                'validate': {
                    'password': {
                        'error': _('Error! Password must contain at least uppercase letter, lowercase letter, numbers and special character.')
                    },
                    'length_between': {
                        'param': [7, 20],
                        'error': _('Error! Password length must be from 8 to 20 characters.')
                    }
                }
            }
        })

        self.__form.process()

        if not self.__form.is_passed():
            return JsonResponse(self.__response.send_private_failure(self.__form.get_errors(with_type=True)))

        register_request = self.__user.get_register_request_by_token(request_data["register_request_token"])

        if not register_request:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Register token is invalid or expired.")
            }]))

        payload = json.loads(register_request.payload)

        if self.__user.username_used(self.__form.get_input_value("username")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Username is already used.")
            }]))

        if self.__user.email_used(self.__form.get_input_value("email")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Email is already used for other account.")
            }]))

        result = self.__user.insert_one({
            "username": self.__form.get_input_value("username"),
            "email": self.__form.get_input_value("email"),
            "first_name": self.__form.get_input_value("first_name"),
            "last_name": self.__form.get_input_value("last_name"),
            "password": self.__form.get_input_value("password"),
            "is_staff": False,
            "is_active": True,
            "is_superuser": True if payload["role"] == "admin" else False
        })

        if result:

            self.__user.delete_register_request_by_token(request_data["register_request_token"])

            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Account created successfully.")
            }]))
        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while creating your account.")
            }]))