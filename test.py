import unittest
from application import app

class TestApplication(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
    
    def tearDown(self):
        pass

    
    def test_home(self):
        result = self.app.get('/', follow_redirects=True)
        self.assertEqual(result.status_code, 200)

    def test_login_display(self):
        response = self.app.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please Login to your account', response.data)
        self.assertIn(b"Username", response.data)

    def test_register_display(self):
        response = self.app.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please Register your account', response.data)
        self.assertIn(b"Username", response.data)

    def login(self, username, password):
        return self.app.post(
            '/login/', 
            data=dict(username=username, password=password), 
            follow_redirects=True
            )   

    def register(self, firstname, lastname, email, username, password, confirm):
        return self.app.post(
            '/register/',
            data=dict(firstname=firstname, lastname=lastname, email=email, username=username, password=password, confirm=confirm),
            follow_redirects=True
            )

    def test_valid_login(self):
        self.app.get('/login/', follow_redirects=True)
        response = self.login('ExampleUser1', 'falconer8')
        self.assertIn(b'ExampleUser1', response.data)


    def test_invalid_login(self):
        self.app.get('/login/', follow_redirects=True)
        response = self.login('ExampleUser123', 'ExamplePassword')
        self.assertIn(b'Login Unsuccessful, Please Try Again', response.data)


if __name__ == '__main__':
    unittest.main()
