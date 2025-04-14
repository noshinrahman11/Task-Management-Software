import unittest
from app import create_app, db_sessions
from TaskManagement.database import Base, engine  # Import Base and engine from your database module

class FlaskTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Create the app and set up the database."""
        cls.app = create_app()  # This creates the Flask app instance
        cls.client = cls.app.test_client()  # This creates the test client
        
        # Set up the application context
        with cls.app.app_context():
            # Use Base.metadata.create_all() to create the tables
            Base.metadata.create_all(bind=engine)  # Creates tables using the engine

    @classmethod
    def tearDownClass(cls):
        """Clean up the database after tests."""
        with cls.app.app_context():
            # Use Base.metadata.drop_all() to drop the tables after the tests
            Base.metadata.drop_all(bind=engine)  # Drops tables using the engine

    def test_register_user(self):
        """Test registering a new user"""
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'Password123!',
            'FirstName': 'Test',
            'LastName': 'User',
            'BirthDate': '2025-03-22 00:00:00',
            'Role': 'Staff'
        })
        # Assert that the status code is 302 (Redirected after successful registration)
        self.assertEqual(response.status_code, 302)
        # Assert that the registration success message is in the response
        self.assertIn(b"Registration successful!", response.data)

    def test_login_user(self):
        """Test login"""
        # First, we need to register the user before testing login.
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'Password123!',
            'FirstName': 'Test',
            'LastName': 'User',
            'BirthDate': '2025-03-22 00:00:00',
            'Role': 'Staff'
        })
        
        response = self.client.post('/login', data={
            'identifier': 'testuser@example.com',  # Or username
            'password': 'Password123!'
        })
        
        # Assert that the status code is 302 (Redirected after successful login)
        self.assertEqual(response.status_code, 302)
        # Assert that the login success message is in the response
        self.assertIn(b"Welcome!", response.data)

if __name__ == '__main__':
    unittest.main()
