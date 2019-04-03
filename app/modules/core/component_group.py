"""
Component Group Module
"""

# local Django
from app.modules.util.helpers import Helpers
from app.modules.entity.component_group_entity import Component_Group_Entity
from app.modules.entity.component_entity import Component_Entity


class Component_Group():

    __component_group_entity = None
    __component_entity = None
    __helpers = None
    __logger = None

    def __init__(self):
        self.__component_group_entity = Component_Group_Entity()
        self.__component_entity = Component_Entity()
        self.__helpers = Helpers()
        self.__logger = self.__helpers.get_logger(__name__)

    def get_one_by_id(self, id):
        group = self.__component_group_entity.get_one_by_id(id)

        if not group:
            return False

        return {
            "id": group.id,
            "name": group.name,
            "uptime": group.uptime,
            "description": group.description,
        }

    def insert_one(self, group):
        return self.__component_group_entity.insert_one(group)

    def update_one_by_id(self, id, group_data):
        return self.__component_group_entity.update_one_by_id(id, group_data)

    def count_all(self):
        return self.__component_group_entity.count_all()

    def count_components(self, group_id):
        return self.__component_entity.count(group_id)

    def get_all(self, offset=None, limit=None):
        return self.__component_group_entity.get_all(offset, limit)

    def delete_one_by_id(self, id):
        self.__component_entity.clear_group(id)
        return self.__component_group_entity.delete_one_by_id(id)
