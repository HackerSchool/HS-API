import unittest 
from unittest.mock import Mock

from app.roles.roles_handler import RolesHandler

class RolesTest(unittest.TestCase):
    def setUp(self):
        self.instance = RolesHandler()
        mock_app = Mock()
        mock_app.config = {'ROLES_PATH': 'tests/roles/roles_test.json'}
        self.instance.init_app(mock_app)

    def test_init_app(self):
        print(self.instance.roles)
        self.assertEqual(self.instance.roles, {
            "coordinator": (0, {"read member", "create member", "edit member", "delete member"}),
            "member":      (1, {"read member", "edit member"})
        })

    def test_has_permission_coord_create(self):
        self.assertTrue(self.instance.has_permission(["coordinator"], "create member"))

    def test_has_permission_mem_create(self):
        self.assertFalse(self.instance.has_permission(["member"], "create member"))

    def test_has_permission_coord_throw(self):
        self.assertFalse(self.instance.has_permission(["coordinator"], "throw member"))

    def test_has_permission_mem_read(self):
        self.assertTrue(self.instance.has_permission(["member"], "read member"))

    def test_has_permission_none_read(self):
        self.assertFalse(self.instance.has_permission([], "read member"))

    def test_has_permission_mem_nothing(self):
        self.assertFalse(self.instance.has_permission(["member"], ""))

    def test_has_permission_none_nothing(self):
        self.assertFalse(self.instance.has_permission([], ""))

    def test_higher_lvl_member_coord(self):
        self.assertFalse(self.instance.has_higher_level(["member"], "coordinator"))

    def test_higher_lvl_coord_mem(self):
        self.assertTrue(self.instance.has_higher_level(["coordinator"], "member"))

    def test_higher_lvl_mem_mem(self):
        self.assertFalse(self.instance.has_higher_level(["member"], "member"))

    def test_higher_lvl_mem_and_coord_mem(self):
        self.assertTrue(self.instance.has_higher_level(["member", "coordinator"], "member"))
 
    def test_higher_lvl_none_mem(self):
        self.assertFalse(self.instance.has_higher_level([], "member"))

    def test_higher_lvl_none_none(self):
        self.assertFalse(self.instance.has_higher_level([], ""))

    def test_higher_lvl_coordinator_none(self):
        self.assertTrue(self.instance.has_higher_level(["coordinator"], ""))