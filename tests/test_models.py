# tests/test_models.py

import datetime
import unittest

from flask_login import current_user

from project import bcrypt
from project.util import BaseTestCase
from project.models import User


class TestUser(BaseTestCase):

    def testUserRegister(self):
        # Scenario which tests user registration and existing data in database
        with self.client:
            self.client.post('/register',
                data=dict(
                    email='dummy@mail.cz',
                    username='Dummy',
                    password='StrongPassword',
                    confirm='StrongPassword'
                ),
                follow_redirects=True
            )

            user = User.query.filter_by(email='dummy@mail.cz').first()

            self.assertTrue(user.id)
            self.assertTrue(user.email == 'dummy@mail.cz')
            self.assertTrue(user.username == 'Dummy')
            self.assertFalse(user.admin)

    def testCheckAdminId(self):
        # Since first account created is ad@min.com, check that its id is equal to 1
        with self.client:
            self.client.post('/login',
                data=dict(
                    email='ad@min.com',
                    password='admin_user'
                ),
                follow_redirects=True
            )

            self.assertTrue(current_user.id == 1)

    def testUserPasswordInDB(self):
        # Scenario which tests admin password in database
        user = User.query.filter_by(email='ad@min.com').first()

        self.assertTrue(bcrypt.check_password_hash(user.password, 'admin_user'))
        self.assertFalse(bcrypt.check_password_hash(user.password, 'falsePass123'))

    def testLoginInvalidPassword(self):
        # Scenario which tests attempt to login with invalid username/password
        with self.client:
            response = self.client.post('/login',
                data=dict(
                    email='ad@min.com',
                    password='IncorrectPassword'
                ),
                follow_redirects=True
            )

        self.assertIn(b'Entered email and password did not match our records.', response.data)


if __name__ == '__main__':
    unittest.main()