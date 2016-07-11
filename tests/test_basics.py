import unittest
from flask import current_app
from programe.app import create_app, db
from programe.app.models import User, Role, Permission, AnonymousUser


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def test_generate_password_hash(self):
        u = User()
        u.password = 'cat'
        self.assertTrue(u.password_hash is not None)

    def test_no_password(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertFalse(u1.password_hash == u2.password_hash)

    def test_roles_permissions(self):
        Role.insert_roles()
        u = User(email='zxc@qq.com', password='123')
        self.assertTrue(u.can(Permission.ADMINISTER))
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        u1 = User(email='qwe@qq.com', password='123')
        self.assertFalse(u1.can(Permission.ADMINISTER))
        self.assertTrue(u1.can(Permission.WRITE_ARTICLES))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()