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
from django.urls import reverse
from pyvalitron.form import Form
from django.http import JsonResponse
from django.utils.translation import gettext as _

# Local Library
from app.modules.util.helpers import Helpers
from app.modules.core.request import Request
from app.modules.core.response import Response
from app.modules.core.user import User as UserModule
from app.modules.validation.extension import ExtraRules
from app.modules.core.decorators import allow_if_authenticated_and_has_permission


class Users(View):
    """Create and List Users Private Endpoint Controller"""

    def __init__(self):
        self.__request = Request()
        self.__response = Response()
        self.__helpers = Helpers()
        self.__form = Form()
        self.__user = UserModule()
        self.__logger = self.__helpers.get_logger(__name__)
        self.__user_id = None
        self.__correlation_id = ""
        self.__form.add_validator(ExtraRules())

    @allow_if_authenticated_and_has_permission("manage_settings")
    def post(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__request.set_request(request)

        request_data = self.__request.get_request_data("post", {
            "invitation": "",
            "first_name": "",
            "last_name": "",
            "username": "",
            "role": "",
            "email": "",
            "password": ""
        })

        if request_data["invitation"] != "":

            self.__form.add_inputs({
                'first_name': {
                    'value': request_data["first_name"],
                    'sanitize': {
                        'strip': {}
                    },
                    'validate': {
                        'sv_names': {
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
                        'sv_names': {
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
                        'strip': {}
                    },
                    'validate': {
                        'sv_email': {
                            'error': _('Error! User email is invalid.')
                        }
                    }
                },
                'password': {
                    'value': request_data["password"],
                    'validate': {
                        'sv_password': {
                            'error': _('Error! Password must contain at least uppercase letter, lowercase letter, numbers and special character.')
                        },
                        'length_between': {
                            'param': [7, 20],
                            'error': _('Error! Password length must be from 8 to 20 characters.')
                        }
                    }
                },
                'role': {
                    'value': request_data["role"],
                    'validate': {
                        'any_of': {
                            'param': [["admin", "user"]],
                            'error': _('Error! Role is invalid.')
                        }
                    }
                }
            })

        else:

            self.__form.add_inputs({
                'email': {
                    'value': request_data["email"],
                    'sanitize': {
                        'strip': {}
                    },
                    'validate': {
                        'sv_email': {
                            'error': _('Error! User email is invalid.')
                        }
                    }
                },
                'role': {
                    'value': request_data["role"],
                    'validate': {
                        'any_of': {
                            'param': [["admin", "user"]],
                            'error': _('Error! Role is invalid.')
                        }
                    }
                }
            })

        self.__form.process()

        if not self.__form.is_passed():
            return JsonResponse(self.__response.send_errors_failure(self.__form.get_errors(), {}, self.__correlation_id))

        if self.__user.email_used(self.__form.get_sinput("email")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Email is already used for other account.")
            }], {}, self.__correlation_id))

        if request_data["invitation"] != "" and self.__user.username_used(self.__form.get_sinput("username")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Username is already used.")
            }], {}, self.__correlation_id))

        if request_data["invitation"] != "":

            result = self.__user.insert_one({
                "username": self.__form.get_sinput("username"),
                "email": self.__form.get_sinput("email"),
                "first_name": self.__form.get_sinput("first_name"),
                "last_name": self.__form.get_sinput("last_name"),
                "password": self.__form.get_sinput("password"),
                "is_staff": False,
                "is_active": True,
                "is_superuser": True if self.__form.get_sinput("role") == "admin" else False
            })

            if result:
                return JsonResponse(self.__response.send_private_success([{
                    "type": "success",
                    "message": _("Account created successfully.")
                }], {}, self.__correlation_id))
            else:
                return JsonResponse(self.__response.send_private_failure([{
                    "type": "error",
                    "message": _("Error! Something goes wrong while creating your account.")
                }], {}, self.__correlation_id))
        else:

            self.__user.delete_register_request_by_email(self.__form.get_sinput("email"))

            token = self.__user.create_register_request(
                self.__form.get_sinput("email"),
                self.__form.get_sinput("role")
            )

            if not token:
                return JsonResponse(self.__response.send_private_failure([{
                    "type": "error",
                    "message": _("Error! Something goes wrong while creating reset request.")
                }], {}, self.__correlation_id))

            message = self.__user.send_register_request_message(self.__form.get_sinput("email"), token)

            if not message:
                return JsonResponse(self.__response.send_private_failure([{
                    "type": "error",
                    "message": _("Error! Something goes wrong while sending register request.")
                }], {}, self.__correlation_id))
            else:
                return JsonResponse(self.__response.send_private_success([{
                    "type": "success",
                    "message": _("Register Request instructions sent successfully.")
                }], {}, self.__correlation_id))

    @allow_if_authenticated_and_has_permission("manage_settings")
    def get(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__request.set_request(request)

        request_data = self.__request.get_request_data("get", {
            "offset": 0,
            "limit": 20
        })

        try:
            offset = int(request_data["offset"])
            limit = int(request_data["limit"])
        except Exception:
            offset = 0
            limit = 20

        return JsonResponse(self.__response.send_private_success([], {
            'users': self.__format_users(self.__user.get_all(offset, limit)),
            'metadata': {
                'offset': offset,
                'limit': limit,
                'count': self.__user.count_all()
            }
        }, self.__correlation_id))

    def __format_users(self, users):
        users_list = []

        for user in users:
            users_list.append({
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": "Admin" if user.is_superuser == 1 else "User",
                "created_at": user.date_joined.strftime("%b %d %Y %H:%M:%S"),
                "edit_url": reverse("app.web.admin.user.edit", kwargs={'user_id': user.id}),
                "delete_url": reverse("app.api.private.v1.admin.user.endpoint", kwargs={'user_id': user.id})
            })

        return users_list


class User(View):
    """Update and Delete User Private Endpoint Controller"""

    def __init__(self):
        self.__request = Request()
        self.__response = Response()
        self.__helpers = Helpers()
        self.__form = Form()
        self.__user = UserModule()
        self.__logger = self.__helpers.get_logger(__name__)
        self.__user_id = None
        self.__correlation_id = ""
        self.__form.add_validator(ExtraRules())

    @allow_if_authenticated_and_has_permission("manage_settings")
    def post(self, request, user_id):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__request.set_request(request)

        request_data = self.__request.get_request_data("post", {
            "first_name": "",
            "last_name": "",
            "username": "",
            "role": "",
            "email": "",
            "update_password": "",
            "password": ""
        })

        if request_data["update_password"] == "":
            self.__form.add_inputs({
                'first_name': {
                    'value': request_data["first_name"],
                    'sanitize': {
                        'strip': {}
                    },
                    'validate': {
                        'sv_names': {
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
                        'sv_names': {
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
                        'strip': {}
                    },
                    'validate': {
                        'sv_email': {
                            'error': _('Error! Email is invalid.')
                        }
                    }
                },
                'role': {
                    'value': request_data["role"],
                    'validate': {
                        'any_of': {
                            'param': [["admin", "user"]],
                            'error': _('Error! Role is invalid.')
                        }
                    }
                }
            })
        else:
            self.__form.add_inputs({
                'first_name': {
                    'value': request_data["first_name"],
                    'sanitize': {
                        'strip': {}
                    },
                    'validate': {
                        'sv_names': {
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
                        'sv_names': {
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
                        'strip': {}
                    },
                    'validate': {
                        'sv_email': {
                            'error': _('Error! Email is invalid.')
                        }
                    }
                },
                'password': {
                    'value': request_data["password"],
                    'validate': {
                        'sv_password': {
                            'error': _('Error! Password must contain at least uppercase letter, lowercase letter, numbers and special character.')
                        },
                        'length_between': {
                            'param': [7, 20],
                            'error': _('Error! Password length must be from 8 to 20 characters.')
                        }
                    }
                },
                'role': {
                    'value': request_data["role"],
                    'validate': {
                        'any_of': {
                            'param': [["admin", "user"]],
                            'error': _('Error! Role is invalid.')
                        }
                    }
                }
            })

        self.__form.process()

        if not self.__form.is_passed():
            return JsonResponse(self.__response.send_errors_failure(self.__form.get_errors(), {}, self.__correlation_id))

        if self.__user.username_used_elsewhere(user_id, self.__form.get_sinput("username")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Username is already used.")
            }], {}, self.__correlation_id))

        if self.__user.email_used_elsewhere(user_id, self.__form.get_sinput("email")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Email is already used for other account.")
            }], {}, self.__correlation_id))

        if request_data["update_password"] == "":

            result = self.__user.update_one_by_id(user_id, {
                "username": self.__form.get_sinput("username"),
                "email": self.__form.get_sinput("email"),
                "first_name": self.__form.get_sinput("first_name"),
                "last_name": self.__form.get_sinput("last_name"),
                "is_superuser": True if self.__form.get_sinput("role") == "admin" else False
            })

        else:

            result = self.__user.update_one_by_id(user_id, {
                "username": self.__form.get_sinput("username"),
                "email": self.__form.get_sinput("email"),
                "first_name": self.__form.get_sinput("first_name"),
                "last_name": self.__form.get_sinput("last_name"),
                "password": self.__form.get_sinput("password"),
                "is_superuser": True if self.__form.get_sinput("role") == "admin" else False
            })

        if result:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("User updated successfully.")
            }], {}, self.__correlation_id))
        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while creating your account.")
            }], {}, self.__correlation_id))

    @allow_if_authenticated_and_has_permission("manage_settings")
    def delete(self, request, user_id):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__user_id = request.user.id

        if self.__user_id == user_id:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! You can't delete your account.")
            }], {}, self.__correlation_id))

        if self.__user.delete_one_by_id(user_id):
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("User deleted successfully.")
            }], {}, self.__correlation_id))

        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while deleting a user.")
            }], {}, self.__correlation_id))
