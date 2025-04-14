import unittest
from app import app, db_sessions
from TaskManagement.models import User, Task

class TestTaskCreation(unittest.TestCase):

    def setUp(self):
        """Set up the test environment"""
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Create a new user for testing
        self.new_user = User(username="testuser", email="test@example.com", password="Password123")
        db_sessions.add(self.new_user)
        db_sessions.commit()

    def test_create_task(self):
        """Test creating a new task"""
        response = self.client.post('/dashboard', data={
            'taskName': 'New Task',
            'description': 'Test Task Description',
            'startDate': '2025-03-01T10:00',
            'dueDate': '2025-03-01T12:00',
            'category': 'General',
            'status': 'Pending',
            'priority': 'High',
            'assignedTo': self.new_user.id
        })
        
        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard after task creation

        # Verify that the task has been added to the database
        task = db_sessions.query(Task).filter_by(name='New Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'New Task')
        self.assertEqual(task.assignedTo, self.new_user.id)

if __name__ == '__main__':
    unittest.main()
