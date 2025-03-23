from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from login import login_manager
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# NOTE: Define tables with no foreign keys first

# Table for users
class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(200))
    FirstName = Column(String(50), unique=True)
    LastName = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    BirthDate = Column(DateTime)
    Role = Column(String(20))

    def __init__(self, username=None, password=None, FirstName=None, LastName=None, email=None, BirthDate=None, Role=None):
        self.username = username
        self.set_password(password)
        self.FirstName = FirstName
        self.LastName = LastName
        self.email = email
        self.BirthDate = BirthDate
        self.Role = Role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_password(self):
        return self.password
    
    def get_id(self):
        return self.id
    

# Table for tasks
class Task(Base):
    __tablename__ = 'tasks'
    task_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(140))
    startDate = Column(DateTime)
    dueDate = Column(DateTime)
    category = Column(String(20))
    status = Column(String(20))
    priority = Column(String(10))
    assignedTo = Column(Integer, ForeignKey('users.id'))

    def __init__(self, name=None, description=None, startDate=None, dueDate=None, category=None, status=None, priority=None, assignedTo=None):
        self.name = name
        self.description = description
        self.startDate = startDate
        self.dueDate = dueDate
        self.category = category
        self.status = status
        self.priority = priority
        self.assignedTo = assignedTo

# Table for projects
class Project(Base):
    __tablename__ = 'projects'
    project_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(140))
    status = Column(Integer)
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)

    def __init__(self, name=None, description=None, status=None, StartDate=None, EndDate=None):
        self.name = name
        self.description = description
        self.status = status
        self.StartDate = StartDate
        self.EndDate = EndDate
        

# Table for many-to-many relationship between users and tasks
class UserTask(Base):
    __tablename__ = 'user_tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))

    user = relationship("User", backref="user_tasks")
    task = relationship("Task", backref="user_tasks")

    def __init__(self, user_id=None, task_id=None):
        self.user_id = user_id
        self.task_id = task_id


# Table for many-to-many relationship between users and projects
class UserProject(Base):
    __tablename__ = 'user_projects'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))

    user = relationship("User", backref="user_projects")
    task = relationship("Project", backref="user_projects")

    def __init__(self, user_id=None, project_id=None):
        self.user_id = user_id
        self.project_id = project_id

# Table for many-to-many relationship between projects and tasks
class ProjectTask(Base):
    __tablename__ = 'project_tasks'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))

    project = relationship("Project", backref="project_tasks")
    task = relationship("Task", backref="project_tasks")

    def __init__(self, project_id=None, task_id=None):
        self.project_id = project_id
        self.task_id = task_id