from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class UserRegistrationTestCase(APITestCase):
    def test_valid_user_registration(self):
        # Test valid user registration
        data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'testpassword'}
        response = self.client.post('/register/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue('username' in response.data)
        self.assertTrue('email' in response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_missing_fields_registration(self):
        # Test registration with missing fields
        data = {'username': 'testuser'}
        response = self.client.post('/register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_existing_user_registration(self):
        # Test registration with an existing username
        user = User.objects.create_user(username='existinguser', email='existing@example.com', password='testpassword')
        data = {'username': 'existinguser', 'email': 'existing@example.com', 'password': 'testpassword'}
        response = self.client.post('/register/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0], 'A user with that username already exists.')