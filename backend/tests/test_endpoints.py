import unittest
from flask import json
from ..app import create_app


class UserRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.token = self.login_user()

    def login_user(self):
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        return response.get_json().get('token')

    def test_register_user(self):
        response = self.client.post('/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully', str(response.data))

    def test_login_user(self):
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.get_json())

    def test_get_users(self):
        response = self.client.get('/users', headers={
            'Authorization': f'Bearer {self.token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_add_patient(self):
        response = self.client.post('/patients/add', json={
            'name': 'John Doe',
            'age': 30,
            'gender': 'Male',
            'contact_number': '1234567890',
            'email': 'john.doe@example.com'
        }, headers={
            'Authorization': f'Bearer {self.token}'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('Patient added successfully', str(response.data))

    def test_get_patients(self):
        response = self.client.get('/patients/', headers={
            'Authorization': f'Bearer {self.token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

if __name__ == '__main__':
    unittest.main()
