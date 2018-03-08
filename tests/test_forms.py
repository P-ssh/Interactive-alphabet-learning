# tests/test_forms.py

import unittest

from project.util import BaseTestCase
from project.user.forms import RegisterForm, LoginForm


class TestRegisterForm(BaseTestCase):

    def testUserRegister(self):
        # Scenario with correct user data
        form = RegisterForm(
            email='dummy@mail.cz', 
            username='Dummy',
            password='StrongPassword', 
            confirm='StrongPassword'
        )
        self.assertTrue(form.validate())

    def testUserRegisterPasswordDoesNotMatch(self):
        # Scenario with non-matching user password
        form = RegisterForm(
            email='dummy@mail.cz',
            username='Dummy',
            password='StrongPassword',
            confirm='strongpassword'
            )
        self.assertFalse(form.validate())

    def testUserRegisterShortPasswordLength(self):
        # Scenario with short password
        form = RegisterForm(
            email='dummy@mail.cz',
            username='Dummy',
            password='abc',
            confirm='abc'
            )
        self.assertFalse(form.validate())

    def testEmailAlreadyRegistered(self):
        # Scenario with attempt to register using already registered email address
        form = RegisterForm(
            email='ad@min.com',
            username='admin',
            password='admin_user',
            confirm='admin_user'
        )
        self.assertFalse(form.validate())


class TestLoginForm(BaseTestCase):

    def testUserLogin(self):
        # Scenario with existing correct user data
        form = LoginForm(
            email='ad@min.com',
            password='admin_user'
        )
        self.assertTrue(form.validate())

    def testUserLoginInvalidEmailOrPassword(self):
        # Scenario with invalid email format
        form = LoginForm(
            email='dummy@email',
            password='StrongPassword'
        )
        self.assertFalse(form.validate())


if __name__ == '__main__':
    unittest.main()