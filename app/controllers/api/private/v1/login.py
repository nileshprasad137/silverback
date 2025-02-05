# Copyright 2019 Silverbackhq
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Third Party Library
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext as _

# Local Library
from pyvalitron.form import Form
from app.modules.util.helpers import Helpers
from app.modules.core.request import Request
from app.modules.core.response import Response
from app.modules.validation.extension import ExtraRules
from app.modules.core.login import Login as LoginModule
from app.modules.core.decorators import stop_request_if_authenticated


class Login(View):
    """Login Private Endpoint Controller"""

    def __init__(self):
        self.__request = Request()
        self.__response = Response()
        self.__helpers = Helpers()
        self.__form = Form()
        self.__login = LoginModule()
        self.__logger = self.__helpers.get_logger(__name__)
        self.__correlation_id = ""
        self.__form.add_validator(ExtraRules())

    @stop_request_if_authenticated
    def post(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""

        if self.__login.is_authenticated(request):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! User is already authenticated.")
            }], {}, self.__correlation_id))

        self.__request.set_request(request)

        request_data = self.__request.get_request_data("post", {
            "username": "",
            "password": ""
        })

        self.__form.add_inputs({
            'username': {
                'value': request_data["username"],
                'sanitize': {
                    'strip': {}
                },
                'validate': {
                    'sv_username_or_email': {
                        'error': _("Error! Username or password is invalid.")
                    }
                }
            },
            'password': {
                'value': request_data["password"],
                'validate': {
                    'sv_password': {
                        'error': _("Error! Username or password is invalid.")
                    },
                    'length_between': {
                        'param': [7, 20],
                        'error': _("Error! Username or password is invalid.")
                    }
                }
            }
        })

        self.__form.process()

        if not self.__form.is_passed():
            return JsonResponse(self.__response.send_errors_failure(self.__form.get_errors(), {}, self.__correlation_id))

        if self.__login.authenticate(self.__form.get_sinput("username"), self.__form.get_sinput("password"), request):
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("You logged in successfully.")
            }], {}, self.__correlation_id))
        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Username or password is invalid.")
            }], {}, self.__correlation_id))
