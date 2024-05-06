from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from io import BytesIO
from PIL import Image as PILImage

from api.serializers import MAX_FILE_SIZE_MB
from .models import Ticket, Image


class UserRegistrationTestCase(APITestCase):
    def test_valid_user_registration(self):
        # Test valid user registration
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
        }
        url = reverse('user_registration')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue('username' in response.data)
        self.assertTrue('email' in response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_missing_fields_registration(self):
        # Test registration with missing fields
        data = {'username': 'testuser'}
        url = reverse('user_registration')
        response = self.client.post(url, data, format='json')
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
        url = reverse('user_registration')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['username'][0], 'A user with that username already exists.'
        )

    def test_weak_password_registration(self):
        # Test registration with a weak password
        data = {'username': 'weakuser', 'email': 'weak@example.com', 'password': 'weak'}
        url = reverse('user_registration')
        response = self.client.post(url, data, format='json')
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
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')

    def test_create_ticket(self):
        data = {
            'title': 'Test Ticket',
            'description': 'Test Description',
            'num_images': 1,
        }
        url = reverse('ticket_list_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(Ticket.objects.get().title, 'Test Ticket')

    def test_list_tickets(self):
        Ticket.objects.create(
            title='Ticket 1', description='Description 1', user=self.user, num_images=1
        )
        Ticket.objects.create(
            title='Ticket 2', description='Description 2', user=self.user, num_images=2
        )
        url = reverse('ticket_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_tickets_by_status(self):
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
        url = reverse('ticket_list_create')
        response = self.client.get(url + '?status=COMPLETED', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Ticket 3')

    def test_filter_tickets_by_created_at(self):
        Ticket.objects.create(
            title='Ticket 1', description='Description 1', user=self.user, num_images=1
        )
        Ticket.objects.create(
            title='Ticket 2', description='Description 2', user=self.user, num_images=2
        )
        url = reverse('ticket_list_create')
        response = self.client.get(
            url + '?created_at__gte=2024-01-01', format='json'
        )  # Assuming date format
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_ticket_missing_fields(self):
        # Test creating a ticket with missing fields
        data = {}
        url = reverse('ticket_list_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_ticket_invalid_num_images(self):
        # Test creating a ticket with invalid num_images
        data = {
            'title': 'Test Ticket',
            'description': 'Test Description',
            'num_images': 0,
        }
        url = reverse('ticket_list_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_list_tickets_empty(self):
        # Test listing tickets when no tickets exist
        url = reverse('ticket_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_filter_tickets_invalid_status(self):
        # Test filtering tickets with an invalid status
        Ticket.objects.create(
            title='Ticket 1', description='Description 1', user=self.user, num_images=1
        )
        url = reverse('ticket_list_create')
        response = self.client.get(url + '?status=INVALID', format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['status'][0],
            'Select a valid choice. INVALID is not one of the available choices.',
        )

    def test_create_ticket_unauthenticated(self):
        # Test creating a ticket without authentication
        self.client.credentials()
        data = {
            'title': 'Test Ticket',
            'description': 'Test Description',
            'num_images': 1,
        }
        url = reverse('ticket_list_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tickets_unauthenticated(self):
        # Test listing tickets without authentication
        self.client.credentials()
        url = reverse('ticket_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_tickets_unauthenticated(self):
        # Test filtering tickets without authentication
        self.client.credentials()
        url = reverse('ticket_list_create')
        response = self.client.get(url + '?status=CREATED', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TicketImagesAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpassword'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        self.ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test Description',
            user=self.user,
            num_images=1,
        )

    def create_image_file(self):
        # Create a test image file
        file = BytesIO()
        image = PILImage.new('RGB', (100, 100))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_upload_image(self):
        url = reverse('ticket_images', kwargs={'ticket_id': self.ticket.id})
        image_file = self.create_image_file()
        data = {'image': image_file}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.filter(ticket=self.ticket).count(), 1)

    def test_upload_image_invalid_format(self):
        url = reverse('ticket_images', kwargs={'ticket_id': self.ticket.id})
        # Create a non-image file
        data = {'image': BytesIO(b'Not an image')}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_exceeds_max_size(self):
        url = reverse('ticket_images', kwargs={'ticket_id': self.ticket.id})
        # Create a large image file (exceeds the maximum size)
        data = {'image': BytesIO(b'0' * (MAX_FILE_SIZE_MB * 1024 * 1024 + 1))}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        url = reverse('ticket_images', kwargs={'ticket_id': self.ticket.id})
        image_file = self.create_image_file()
        data = {'image': image_file}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
