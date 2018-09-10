import os
import unittest
import tempfile
from HonoursProject import application
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

    def login(self, username, password):
        return self.app.post(
            '/login/', 
            data=dict(username=username, password=password), 
            follow_redirects=True
            )

    def test_login_display(self):
        response = self.app.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please Login to your account', response.data)
        self.assertIn(b"Username", response.data)
    
    def test_valid_login(self):
        self.app.get('/login/', follow_redirects=True)
        response = self.login('ExampleUser1', 'falconer8')
        self.assertIn(b'ExampleUser1', response.data)


if __name__ == '__main__':
    unittest.main()


