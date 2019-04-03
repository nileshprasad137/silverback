"""
Incident Update Module
"""

# local Django
from app.modules.util.helpers import Helpers
from app.modules.entity.incident_update_entity import Incident_Update_Entity
from app.modules.entity.incident_entity import Incident_Entity


class Incident_Update():

    __incident_update_entity = None
    __incident_entity = None
    __helpers = None
    __logger = None

    def __init__(self):
        self.__incident_update_entity = Incident_Update_Entity()
        self.__incident_entity = Incident_Entity()
        self.__helpers = Helpers()
        self.__logger = self.__helpers.get_logger(__name__)

    def get_one_by_id(self, id):
        update = self.__incident_update_entity.get_one_by_id(id)

        if not update:
            return False

        return {
            "id": update.id,
            "datetime": update.datetime,
            "message": update.message,
            "notify_subscribers": update.notify_subscribers,
            "total_suscribers": update.total_suscribers,
            "status": update.status
        }

    def insert_one(self, update):
        return self.__incident_update_entity.insert_one(update)

    def update_one_by_id(self, id, update_data):
        return self.__incident_update_entity.update_one_by_id(id, update_data)

    def count_all(self, incident_id):
        return self.__incident_update_entity.count_all(incident_id)

    def get_all(self, incident_id, offset=None, limit=None):
        return self.__incident_update_entity.get_all(incident_id, offset, limit)

    def delete_one_by_id(self, id):
        return self.__incident_update_entity.delete_one_by_id(id)
