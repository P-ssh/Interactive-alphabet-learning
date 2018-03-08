import os
import unittest
import coverage

#from flask.ext.script import Manager
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
#from flask.ext.migrate import Migrate, MigrateCommand

from project import app, db
from project.models import *

app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """This method runs unit tests without the coverage.    """

    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    else:
        return 1


@manager.command
def coverageTest():
    """This method runs unit tests with the coverage."""

    cov = coverage.coverage(branch=True, include='project/*')
    cov.start()
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    print('Coverage Summary:')
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'tmp/coverage')
    cov.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    cov.erase()


@manager.command
def create_db():
    """This method creates the database."""

    db.create_all()
    

@manager.command
def drop_db():
    """This method drops the database."""
    db.drop_all()


if __name__ == '__main__':
    manager.run()