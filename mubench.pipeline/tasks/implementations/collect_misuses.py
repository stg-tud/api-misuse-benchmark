from data.project_version import ProjectVersion
from utils.data_entity_lists import DataEntityLists


class CollectMisusesTask:
    def run(self, version: ProjectVersion, data_entity_lists: DataEntityLists):
        return [misuse for misuse in version.misuses
                if not self.__is_filtered(version.id, misuse.id, data_entity_lists)]

    @staticmethod
    def __is_filtered(version_id: str, misuse_id: str, data_entity_lists: DataEntityLists) -> bool:
        white_list = data_entity_lists.get_misuse_white_list(version_id)
        black_list = data_entity_lists.black_list

        is_whitelisted = not white_list or white_list.case_insensitive_contains(misuse_id)
        is_blacklisted = black_list.case_insensitive_contains(misuse_id)
        return is_blacklisted or not is_whitelisted
