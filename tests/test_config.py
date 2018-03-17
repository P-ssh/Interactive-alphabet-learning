# tests/test_config.py

from project import app

from flask import current_app
from flask_testing import TestCase
import unittest


class TestTestingConfig(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def testAppConfig(self):
        self.assertTrue(current_app.config['TESTING'])
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 1)
        self.assertTrue(app.config['WTF_CSRF_ENABLED'] is False)

    def testAppNotNone(self):
        self.assertFalse(current_app is None)


if __name__ == '__main__':
    unittest.main()
