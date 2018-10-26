import os
import unittest
from application import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from application import app, Course, User, LessonData, Lesson, Quiz
from application import db

class TestApplication(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kevin/HonoursProject/tests/testDB.db'
        app.config['DEBUG'] = False
        self.app = app.test_client()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        #pass
    
    def register(self, firstname, lastname, email, username, password, confirm):
        return self.app.post(
            '/register/',
            data=dict(firstname=firstname, lastname=lastname, email=email, username=username, password=password, confirm=confirm),
            follow_redirects=True
            )
   
    def login(self, username, password):
        return self.app.post(
            '/login/', 
            data=dict(username=username, password=password), 
            follow_redirects=True
            ) 
    
    def logout(self):
        return self.app.get('/logout/',
                follow_redirects=True)
        self.assertEqual(response.status_code, 200)


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

    
    def test_valid_registeration(self):
        response = self.register('Kevin', 'Falconer', 'ExampleUSER1234@gmail.com', 'ExampleUser1', 'password', 'password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ExampleUser1', response.data)
    
    def test_valid_login(self):
        response = self.register('Kevin', 'Falconer', 'ExampleUSER1234@gmail.com', 'ExampleUser1', 'password', 'password')
        self.assertEqual(response.status_code, 200)
        self.app.get('/logout/', follow_redirects=True)
        self.app.get('/login/', follow_redirects=True)
        response = self.login('ExampleUser1', 'password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ExampleUser1', response.data)


    def test_invalid_login(self):
        self.app.get('/login/', follow_redirects=True)
        response = self.login('ExampleUser123', 'ExamplePassword')
        self.assertIn(b'Login Unsuccessful, Please Try Again', response.data)

    def test_invalid_registeration(self):
        response = self.register('Kevin', 'Falconer', 'ExampleEmail1234@gmail.com', 'ExampleUser70', 'examplepassword', 'examplepa')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please Register your account', response.data)


    def test_dashboard_without_login(self):
        response = self.app.get('/dashboard/ExampleUser70/', follow_redirects=True)
        self.assertIn(b'Please Login to your account', response.data)

    #def test_dashboard_page(self):
        #response = self.register('Kevin', 'Falconer', 'ExampleUSER1234@gmail.com', 'ExampleUser12', 'password', 'password')
        #self.assertEqual(response.status_code, 200)
        #self.app.get('/logout/', follow_redirects=True)
        #self.app.get('/login/', follow_redirects=True)
        #response = self.login('ExampleUser12', 'password')
        #self.assertEqual(response.status_code, 200)
        #self.assertIn(b'ExampleUser12', response.data)

    def test_course_page(self):
         self.app.get('/register/', follow_redirects=True)
         response = self.register('Kevin', 'Falconer', 'ExampleEmail1234@gmail.com', 'ExampleUser70', 'examplepassword', 'examplepassword')
         self.assertEqual(response.status_code, 200)
         course = Course(11111, 'HTML:Introduction', 'Description', 5)
         db.session.add(course)
         db.session.commit()
         response1 = self.app.get('dashboard/ExampleUser70/course/11111/', follow_redirects=True)
         self.assertIn('Course Page: HTML:Introduction', response1.data)

    def test_template_page(self):
        self.app.get('/register/', follow_redirects=True)
        response = self.register('Kevin', 'Falconer', 'ExampleEmail1234@gmail.com', 'ExampleUser70', 'examplepassword', 'examplepassword')
        self.assertEqual(response.status_code, 200)
        course = Course(11111, 'HTML:Introduction', 'Description', 5)
        db.session.add(course)
        lessondata = LessonData(111,'HTML:Lesson 1',11111)
        db.session.add(lessondata)
        db.session.commit()
        response1 = self.app.get('dashboard/ExampleUser70/course/11111/lesson/111', follow_redirects=True)
        self.assertIn('Lesson: HTML:Lesson 1', response1.data)

    def test_excercise_page(self):
        self.app.get('/register/', follow_redirects=True)
        response = self.register('Kevin', 'Falconer', 'ExampleEmail1234@gmail.com', 'ExampleUser70', 'examplepassword', 'examplepassword')
        self.assertEqual(response.status_code, 200)
        course = Course(11111, 'HTML:Introduction', 'Description', 5)
        db.session.add(course)
        lessondata = LessonData(121,'HTML:Excercise 1',11111)
        db.session.add(lessondata)
        db.session.commit()
        response1 = self.app.get('dashboard/ExampleUser70/course/11111/excercise/121/', follow_redirects=True)
        self.assertIn('Excercise: HTML:Excercise 1', response1.data)

    def test_quiz_page(self):
        self.app.get('/register/', follow_redirects=True)
        response = self.register('Kevin', 'Falconer', 'ExampleEmail1234@gmail.com', 'ExampleUser70', 'examplepassword', 'examplepassword')
        self.assertEqual(response.status_code, 200)
        course = Course(11111, 'HTML:Introduction', 'Description', 5)
        db.session.add(course)
        lessondata = LessonData(131,'HTML:Quiz',11111)
        db.session.add(lessondata)
        db.session.commit()
        response1 = self.app.get('dashboard/ExampleUser70/course/11111/quiz/131/', follow_redirects=True)
        self.assertIn('Which HTML tag will display the largest heading?', response1.data)

    def test_course_without_login(self):
        response = self.app.get('dashboard/ExampleUser70/course/11111/', follow_redirects=True)
        self.assertIn(b'Please Login to your account', response.data)

    def test_template_without_login(self):
        response = self.app.get('dashboard/ExampleUser70/course/11111/lesson/111', follow_redirects=True)
        self.assertIn(b'Please Login to your account', response.data)

    def test_excercise_without_login(self):
        response = self.app.get('dashboard/ExampleUser70/course/11111/excercise/121/', follow_redirects=True)
        self.assertIn(b'Please Login to your account', response.data)

    def test_quiz_without_login(self):
        response = self.app.get('dashboard/ExampleUser70/course/11111/quiz/131/', follow_redirects=True)
        self.assertIn(b'Please Login to your account', response.data)

    def test_database_entry_course(self):
         self.app.get('/register/', follow_redirects=True)
         response = self.register('Kevin', 'Falconer', 'ExampleEmail1234@gmail.com', 'ExampleUser70', 'examplepassword', 'examplepassword')
         self.assertEqual(response.status_code, 200)
         course = Course('HTML:Introduction', 11111,'Description', 'Hello')
         db.session.add(course)
         #db.session.commit()
         self.assertRaises(IntegrityError, db.session.commit)
         #response1 = self.app.get('dashboard/ExampleUser70/course/11111/', follow_redirects=True)
         #self.assertIn('Course Page: HTML:Introduction', response1.data)
if __name__ == '__main__':
    unittest.main()
