import os
import unittest
import tempfile
import application
from application import db

class applicationTestCase(unittest.TestCase):

    def setUp(self):
        #self.db_fd, application.app.config['DATABASE'] = tempfile.mkstemp()
        SQLALCHEMY_DATABASE_URI = 'sqlite:////home/kevin/HonoursProject/db.db'
        TESTING = True
        self.app = application.app.test_client()
        with application.app.app_context():
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()


