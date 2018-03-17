# tests/test_functional.py

from project.util import BaseTestCase

from flask_login import current_user
import unittest




class TestPublic(BaseTestCase):

    def testLoginRequiredMainPage(self):
        # Scenario when non-logged user attempts to visit main page of application
        response = self.client.get('/', follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertIn(b'Please log in to access this page', response.data)

    def testLoginRequiredCoursesPage(self):
        # Scenario when non-logged user attempts to visit courses page
        response = self.client.get('/courses', follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertIn(b'Please log in to access this page', response.data)


class TestLoggingInOut(BaseTestCase):

    def testLogin(self):
        # Scenario which tests logging into application with valid credentials
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(
                    email="ad@min.com",
                    password="admin_user"
                ),
                follow_redirects=True
            )
            self.assertIn(b'Welcome', response.data)
            self.assertTrue(current_user.email == "ad@min.com")
            self.assertTrue(current_user.username == 'admin')
            self.assertTrue(current_user.is_active)
            self.assertTrue(response.status_code == 200)

    def testLogout(self):
        # Scenario which tests logging in and out of the application
        with self.client:
            self.client.post(
                '/login',
                data=dict(
                    email="ad@min.com",
                    password="admin_user"
                ),
                follow_redirects=True
            )
            response = self.client.get('/logout', follow_redirects=True)
            self.assertIn(b'You were logged out.', response.data)
            self.assertFalse(current_user.is_active)


if __name__ == '__main__':
    unittest.main()