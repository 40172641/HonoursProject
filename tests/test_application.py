import os
import unittest
import tempfile
import application

class applicationTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, application.app.config['DATABASE'] = tempfile.mkstemp()
        #self.db_fd, application.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kevin/HonoursProject/database.db'
        application.app.testing = True
        self.app = application.app.test_client()
        with application.app.app_context():
            application.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(application.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries so far' in rv.data
    
if __name__ == '__main__':
    unittest.main()


