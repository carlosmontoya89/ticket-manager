from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Ticket


class UserRegistrationTestCase(APITestCase):
    def test_valid_user_registration(self):
        # Test valid user registration
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
        }
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
        user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpassword',
        )
        data = {
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password': 'testpassword',
        }
        response = self.client.post('/register/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['username'][0], 'A user with that username already exists.'
        )

    def test_weak_password_registration(self):
        # Test registration with a weak password
        data = {'username': 'weakuser', 'email': 'weak@example.com', 'password': 'weak'}
        response = self.client.post('/register/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['password'][0], 'Ensure this field has at least 8 characters.'
        )


class TicketListCreateAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpassword'
        )
        self.token = Token.objects.create(user=self.user)

    def test_create_ticket(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        data = {
            'title': 'Test Ticket',
            'description': 'Test Description',
            'num_images': 1,
        }
        response = self.client.post('/tickets/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(Ticket.objects.get().title, 'Test Ticket')

    def test_list_tickets(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        Ticket.objects.create(
            title='Ticket 1', description='Description 1', user=self.user, num_images=1
        )
        Ticket.objects.create(
            title='Ticket 2', description='Description 2', user=self.user, num_images=2
        )
        response = self.client.get('/tickets/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_filter_tickets_by_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        Ticket.objects.create(
            title='Ticket 1', description='Description 1', user=self.user, num_images=1
        )
        Ticket.objects.create(
            title='Ticket 2', description='Description 2', user=self.user, num_images=2
        )
        Ticket.objects.create(
            title='Ticket 3',
            description='Description 3',
            user=self.user,
            num_images=3,
            status='COMPLETED',
        )
        response = self.client.get('/tickets/?status=COMPLETED', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Ticket 3')

    def test_filter_tickets_by_created_at(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        Ticket.objects.create(
            title='Ticket 1', description='Description 1', user=self.user, num_images=1
        )
        Ticket.objects.create(
            title='Ticket 2', description='Description 2', user=self.user, num_images=2
        )
        response = self.client.get(
            '/tickets/?created_at__gte=2024-01-01', format='json'
        )  # Assuming date format
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_create_ticket_missing_fields(self):
        # Test creating a ticket with missing fields
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        data = {}
        response = self.client.post('/tickets/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_ticket_invalid_num_images(self):
        # Test creating a ticket with invalid num_images
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        data = {
            'title': 'Test Ticket',
            'description': 'Test Description',
            'num_images': 0,
        }
        response = self.client.post('/tickets/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_list_tickets_empty(self):
        # Test listing tickets when no tickets exist
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.get('/tickets/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_filter_tickets_invalid_status(self):
        # Test filtering tickets with an invalid status
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        Ticket.objects.create(
            title='Ticket 1', description='Description 1', user=self.user, num_images=1
        )
        response = self.client.get('/tickets/?status=INVALID', format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['status'][0],
            'Select a valid choice. INVALID is not one of the available choices.',
        )

    def test_create_ticket_unauthenticated(self):
        # Test creating a ticket without authentication
        data = {
            'title': 'Test Ticket',
            'description': 'Test Description',
            'num_images': 1,
        }
        response = self.client.post('/tickets/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tickets_unauthenticated(self):
        # Test listing tickets without authentication
        response = self.client.get('/tickets/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_tickets_unauthenticated(self):
        # Test filtering tickets without authentication
        response = self.client.get('/tickets/?status=CREATED', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
