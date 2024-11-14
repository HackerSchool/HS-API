import unittest 
from unittest.mock import Mock, patch

from app.models import Member
from app.extensions import roles_handler

class MemberModelTest(unittest.TestCase):
    def test_invalid_username(self):
        with self.assertRaises(ValueError):
            Member(
                username="ççç_invalid", 
                password="password", 
                ist_id="istid", 
                name="name", 
                member_number=10, 
                join_date="2014-01-01", 
                course="course", 
                email="email@hackerschool.dev", 
                description="", 
                exit_date="",
                extra="", 
                roles=["member"]
            )
    
    def test_no_roles(self):
        with self.assertRaises(ValueError):
            Member(
                username="username", 
                password="password", 
                ist_id="istid", 
                name="name", 
                member_number=1, 
                join_date="2014-01-01", 
                course="course", 
                email="email@hackerschool.dev", 
                description="", 
                exit_date="",
                extra="", 
                roles=[]
            )
 
    @patch.object(roles_handler, 'exists_role')
    def test_non_existant_role(self, exists_role):
        exists_role.return_value = False # make exists_role return false
        with self.assertRaises(ValueError):
            Member(
                username="username", 
                password="password", 
                ist_id="istid", 
                name="name", 
                member_number=1, 
                join_date="2014-01-01", 
                course="course", 
                email="email@hackerschool.dev", 
                description="", 
                exit_date="",
                extra="", 
                roles=["random role"]
            )
    
    def test_invalid_join_date(self):
        with self.assertRaises(ValueError):
            Member(
                username="username", 
                password="password", 
                ist_id="istid", 
                name="name", 
                member_number=1, 
                join_date="01-01-1000", 
                course="course", 
                email="email@hackerschool.dev", 
                description="", 
                exit_date="",
                extra="", 
                roles=["member"]
            )
