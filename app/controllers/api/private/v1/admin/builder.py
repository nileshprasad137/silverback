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

# Standard Library
import json

# Third Party Library
from django.views import View
from pyvalitron.form import Form
from django.http import JsonResponse
from django.utils.translation import gettext as _

# Local Library
from app.modules.util.helpers import Helpers
from app.modules.core.request import Request
from app.modules.core.response import Response
from app.modules.core.settings import Settings
from app.modules.validation.extension import ExtraRules
from app.modules.core.metric import Metric as MetricModule
from app.modules.core.component import Component as ComponentModule
from app.modules.core.decorators import allow_if_authenticated_and_has_permission
from app.modules.core.component_group import ComponentGroup as ComponentGroupModule


class BuilderSystemMetrics(View):
    """Add and Remove Builder System Metrics Private Endpoint Controller"""

    def __init__(self):
        self.__request = Request()
        self.__response = Response()
        self.__helpers = Helpers()
        self.__settings = Settings()
        self.__metric = MetricModule()
        self.__form = Form()
        self.__logger = self.__helpers.get_logger(__name__)
        self.__user_id = None
        self.__correlation_id = ""
        self.__form.add_validator(ExtraRules())

    @allow_if_authenticated_and_has_permission("manage_settings")
    def post(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__request.set_request(request)
        request_data = self.__request.get_request_data("post", {
            "metric_id": ""
        })

        if request_data["metric_id"] == "" or not self.__metric.get_one_by_id(request_data["metric_id"].replace("m-", "")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Metric is required.")
            }], {}, self.__correlation_id))

        metrics = self.__settings.get_value_by_key(
            "builder_metrics",
            json.dumps([])
        )

        metrics = json.loads(metrics)

        if request_data["metric_id"] in metrics:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Metric added successfully.")
            }], {}, self.__correlation_id))

        metrics.append(request_data["metric_id"])

        result = self.__settings.update_options({
            "builder_metrics": json.dumps(metrics)
        })

        if result:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Metric added successfully.")
            }], {}, self.__correlation_id))

        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while adding metric.")
            }], {}, self.__correlation_id))

    @allow_if_authenticated_and_has_permission("manage_settings")
    def delete(self, request, metric_id):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        metrics = self.__settings.get_value_by_key(
            "builder_metrics",
            json.dumps([])
        )

        metrics = json.loads(metrics)

        if metric_id not in metrics:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Metric deleted successfully.")
            }], {}, self.__correlation_id))

        metrics.remove(metric_id)

        result = self.__settings.update_options({
            "builder_metrics": json.dumps(metrics)
        })

        if result:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Metric deleted successfully.")
            }], {}, self.__correlation_id))

        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while deleting metric.")
            }], {}, self.__correlation_id))


class BuilderComponents(View):
    """Add and Remove Builder Components Private Endpoint Controller"""

    def __init__(self):
        self.__request = Request()
        self.__response = Response()
        self.__helpers = Helpers()
        self.__settings = Settings()
        self.__component = ComponentModule()
        self.__component_group = ComponentGroupModule()
        self.__form = Form()
        self.__logger = self.__helpers.get_logger(__name__)
        self.__user_id = None
        self.__correlation_id = ""
        self.__form.add_validator(ExtraRules())

    @allow_if_authenticated_and_has_permission("manage_settings")
    def post(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__request.set_request(request)
        request_data = self.__request.get_request_data("post", {
            "component_id": ""
        })

        if request_data["component_id"] == "" or ("c-" not in request_data["component_id"] and "g-" not in request_data["component_id"]):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Compnent or compnent group is required.")
            }], {}, self.__correlation_id))

        if "c-" in request_data["component_id"] and not self.__component.get_one_by_id(request_data["component_id"].replace("c-", "")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Compnent or compnent group is required.")
            }], {}, self.__correlation_id))

        if "g-" in request_data["component_id"] and not self.__component_group.get_one_by_id(request_data["component_id"].replace("g-", "")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Compnent or compnent group is required.")
            }], {}, self.__correlation_id))

        components = self.__settings.get_value_by_key(
            "builder_components",
            json.dumps([])
        )

        components = json.loads(components)

        if request_data["component_id"] in components:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Component added successfully.")
            }], {}, self.__correlation_id))

        components.append(request_data["component_id"])

        result = self.__settings.update_options({
            "builder_components": json.dumps(components)
        })

        if result:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Component added successfully.")
            }], {}, self.__correlation_id))

        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while adding component.")
            }], {}, self.__correlation_id))

    @allow_if_authenticated_and_has_permission("manage_settings")
    def delete(self, request, component_id):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        components = self.__settings.get_value_by_key(
            "builder_components",
            json.dumps([])
        )

        components = json.loads(components)

        if component_id not in components:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Component deleted successfully.")
            }], {}, self.__correlation_id))

        components.remove(component_id)

        result = self.__settings.update_options({
            "builder_components": json.dumps(components)
        })

        if result:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Component deleted successfully.")
            }], {}, self.__correlation_id))

        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while deleting component.")
            }], {}, self.__correlation_id))


class BuilderSettings(View):
    """Update Builder Settings Private Endpoint Controller"""

    def __init__(self):
        self.__request = Request()
        self.__response = Response()
        self.__helpers = Helpers()
        self.__settings = Settings()
        self.__form = Form()
        self.__logger = self.__helpers.get_logger(__name__)
        self.__user_id = None
        self.__correlation_id = ""
        self.__form.add_validator(ExtraRules())

    @allow_if_authenticated_and_has_permission("manage_settings")
    def post(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__request.set_request(request)
        request_data = self.__request.get_request_data("post", {
            "builder_headline": "",
            "builder_favicon_url": "",
            "builder_logo_url": "",
            "builder_about": ""
        })

        self.__form.add_inputs({
            'builder_headline': {
                'value': request_data["builder_headline"],
                'sanitize': {
                    'strip': {}
                },
                'validate': {
                    'length_between': {
                        'param': [0, 100],
                        'error': _('Error! Headline is very long.')
                    },
                    'optional': {}
                }
            },
            'builder_favicon_url': {
                'value': request_data["builder_favicon_url"],
                'sanitize': {
                    'strip': {}
                },
                'validate': {
                    'sv_url': {
                        'error': _('Error! Favicon URL is invalid.')
                    }
                }
            },
            'builder_logo_url': {
                'value': request_data["builder_logo_url"],
                'sanitize': {
                    'strip': {}
                },
                'validate': {
                    'sv_url': {
                        'error': _('Error! Logo URL is invalid.')
                    }
                }
            },
            'builder_about': {
                'value': request_data["builder_about"],
                'sanitize': {
                    'strip': {}
                },
                'validate': {
                    'length_between': {
                        'param': [0, 20000],
                        'error': _('Error! About is very long.')
                    },
                    'optional': {}
                }
            },
        })

        self.__form.process()

        if not self.__form.is_passed():
            return JsonResponse(self.__response.send_errors_failure(self.__form.get_errors(), {}, self.__correlation_id))

        result = self.__settings.update_options({
            "builder_headline": self.__form.get_sinput("builder_headline"),
            "builder_favicon_url": self.__form.get_sinput("builder_favicon_url"),
            "builder_logo_url": self.__form.get_sinput("builder_logo_url"),
            "builder_about": self.__form.get_sinput("builder_about")
        })

        if result:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Settings updated successfully.")
            }], {}, self.__correlation_id))

        else:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while updating settings.")
            }], {}, self.__correlation_id))
