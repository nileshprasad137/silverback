"""
Status Page Index Web Controller
"""

# standard library
import os

# Django
from django.http import Http404
from django.views import View
from django.shortcuts import render

# local Django
from app.modules.core.context import Context
from app.modules.entity.option_entity import Option_Entity
from app.modules.core.decorators import redirect_if_not_installed
from app.modules.core.status_page import Status_Page as Status_Page_Module


class Status_Page_Index(View):

    template_name = 'templates/status_page_index.html'
    __context = None
    __option_entity = None
    __status_page_module = None
    __correlation_id = None

    @redirect_if_not_installed
    def get(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__context = Context()
        self.__option_entity = Option_Entity()
        self.__status_page_module = Status_Page_Module()

        self.__context.autoload_options()
        self.__context.push({
            "page_title": self.__context.get("app_name", os.getenv("APP_NAME", "Silverback")),
            "is_authenticated": request.user and request.user.is_authenticated,
            "system_status": self.__status_page_module.get_system_status(),
            "about_site": self.__status_page_module.get_about_site(),
            "logo_url": self.__status_page_module.get_logo_url(),
            "favicon_url": self.__status_page_module.get_favicon_url(),
            "past_incidents": self.__status_page_module.get_past_incidents(7),
            "system_metrics": self.__status_page_module.get_system_metrics(),
            "services": self.__status_page_module.get_services()
        })

        return render(request, self.template_name, self.__context.get())


class Status_Page_History(View):

    template_name = 'templates/status_page_history.html'
    __context = None
    __option_entity = None
    __status_page_module = None
    __correlation_id = None

    @redirect_if_not_installed
    def get(self, request, period):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__context = Context()
        self.__option_entity = Option_Entity()
        self.__status_page_module = Status_Page_Module()

        data = self.__status_page_module.get_incidents_for_period(period)

        if not data:
            raise Http404("History period not found.")

        self.__context.autoload_options()
        self.__context.push({
            "page_title": self.__context.get("app_name", os.getenv("APP_NAME", "Silverback")),
            "logo_url": self.__status_page_module.get_logo_url(),
            "favicon_url": self.__status_page_module.get_favicon_url(),
            "is_authenticated": request.user and request.user.is_authenticated,
            "prev_link": period + 1,
            "next_link": period - 1 if period > 1 else 1,
            "history_period": data["period"],
            "past_incidents": data["incidents"],
        })

        return render(request, self.template_name, self.__context.get())


class Status_Page_Single(View):

    template_name = 'templates/status_page_single.html'
    __context = None
    __option_entity = None
    __status_page_module = None
    __correlation_id = None

    @redirect_if_not_installed
    def get(self, request, uri):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__context = Context()
        self.__option_entity = Option_Entity()
        self.__status_page_module = Status_Page_Module()

        incident = self.__status_page_module.get_incident_by_uri(uri)

        if not incident:
            raise Http404("Incident not found.")

        self.__context.autoload_options()
        self.__context.push({
            "page_title": self.__context.get("app_name", os.getenv("APP_NAME", "Silverback")),
            "logo_url": self.__status_page_module.get_logo_url(),
            "favicon_url": self.__status_page_module.get_favicon_url(),
            "is_authenticated": request.user and request.user.is_authenticated,
            "uri": uri,
            "incident": incident
        })

        return render(request, self.template_name, self.__context.get())
