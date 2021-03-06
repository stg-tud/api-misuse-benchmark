from nose.tools import assert_equals

from utils.data_entity_lists import DataEntityLists


class TestDataEntityLists:
    def test_should_add_all_project_ids(self):
        uut = DataEntityLists(["p1.v.m", "p2.v", "p3"], [])

        actual = uut.get_project_white_list()

        expected = ["p1", "p2", "p3"]
        assert_equals(expected, actual)

    def test_should_add_all_version_ids(self):
        uut = DataEntityLists(["p.v1.m", "p.v2", "p"], [])

        actual = uut.get_version_white_list("p")

        expected = ["p.v1", "p.v2"]
        assert_equals(expected, actual)

    def test_should_add_all_misuse_ids(self):
        uut = DataEntityLists(["p.v1.m1", "p.v2.m1", "p.v2.m2", "p"], [])

        actual = uut.get_misuse_white_list("p.v2")

        expected = ["p.v2.m1", "p.v2.m2"]
        assert_equals(expected, actual)
