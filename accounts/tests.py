from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import CustomerProfile


class AccountsAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse('user-register')
        self.login_url = reverse('token_obtain_pair')  # Adjust if using a different authentication method
        self.profile_url = reverse('user-profile')  # Update with the correct URL name

        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
            "profile": {
                "phone_number": "1234567890",
                "date_of_birth": "1990-01-01"
            }
        }

    def test_user_registration(self):
        """
        Test that a user can register with valid data.
        """
        response = self.client.post(self.registration_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(CustomerProfile.objects.filter(user__username='testuser').exists())

    def test_user_registration_missing_fields(self):
        """
        Test that registration fails when required fields are missing.
        """
        incomplete_data = self.user_data.copy()
        incomplete_data.pop('email')  # Remove the email field
        response = self.client.post(self.registration_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_login(self):
        """
        Test that a user can obtain a JWT token with valid credentials.
        """
        # First, register the user
        self.client.post(self.registration_url, self.user_data, format='json')

        # Attempt to log in
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.token = response.data['access']

    def test_retrieve_user_profile(self):
        """
        Test that an authenticated user can retrieve their profile.
        """
        # Register and log in the user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']

        # Set the token in the headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Retrieve the profile
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'testuser@example.com')
        self.assertEqual(response.data['profile']['phone_number'], '1234567890')
        self.assertEqual(response.data['profile']['date_of_birth'], '1990-01-01')

    def test_update_user_profile(self):
        """
        Test that an authenticated user can update their profile.
        """
        # Register and log in the user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']

        # Set the token in the headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Prepare update data
        update_data = {
            "username": "updateduser",
            "email": "updateduser@example.com",
            "password": "testpassword123",
            "profile": {
                "phone_number": "0987654321",
                "date_of_birth": "1991-02-02"
            }
        }

        # Update the profile
        response = self.client.put(self.profile_url, update_data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the changes
        self.assertEqual(response.data['username'], 'updateduser')
        self.assertEqual(response.data['email'], 'updateduser@example.com')
        self.assertEqual(response.data['profile']['phone_number'], '0987654321')
        self.assertEqual(response.data['profile']['date_of_birth'], '1991-02-02')

    def test_unauthenticated_profile_access(self):
        """
        Test that an unauthenticated user cannot access the profile endpoint.
        """
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_username_registration(self):
        """
        Test that registering with a duplicate username fails.
        """
        # Register the first user
        self.client.post(self.registration_url, self.user_data, format='json')

        # Attempt to register a second user with the same username
        duplicate_user_data = self.user_data.copy()
        duplicate_user_data['email'] = 'anotheremail@example.com'  # Change email to avoid duplicate
        response = self.client.post(self.registration_url, duplicate_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_duplicate_email_registration(self):
        """
        Test that registering with a duplicate email fails.
        """
        # Register the first user
        self.client.post(self.registration_url, self.user_data, format='json')

        # Attempt to register a second user with the same email
        duplicate_user_data = self.user_data.copy()
        duplicate_user_data['username'] = 'anotheruser'  # Change username to avoid duplicate
        response = self.client.post(self.registration_url, duplicate_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_password_write_only(self):
        """
        Test that the password is write-only and not returned in responses.
        """
        # Register the user
        response = self.client.post(self.registration_url, self.user_data, format='json')
        self.assertNotIn('password', response.data)

        # Log in the user
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        self.assertNotIn('password', response.data)

        # Retrieve the profile
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.profile_url)
        self.assertNotIn('password', response.data)

    def test_partial_update_user_profile(self):
        """
        Test that an authenticated user can partially update their profile.
        """
        # Register and log in the user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Prepare partial update data
        partial_update_data = {
            "profile": {
                "phone_number": "1112223333"
            }
        }

        # Partially update the profile
        response = self.client.patch(self.profile_url, partial_update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the changes
        self.assertEqual(response.data['profile']['phone_number'], '1112223333')
        # Ensure other fields remain unchanged
        self.assertEqual(response.data['profile']['date_of_birth'], '1990-01-01')

    def test_invalid_date_of_birth(self):
        """
        Test that registration fails with an invalid date of birth.
        """
        invalid_data = self.user_data.copy()
        invalid_data['profile']['date_of_birth'] = 'invalid-date'
        response = self.client.post(self.registration_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_of_birth', response.data['profile'])

    def test_update_password(self):
        """
        Test that a user can update their password.
        """
        # Register and log in the user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Prepare password update data
        update_data = self.user_data.copy()
        update_data['password'] = 'newpassword123'


        # Update the password
        response = self.client.put(self.profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Log out
        self.client.credentials()

        # Attempt to log in with the old password
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Log in with the new password
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "newpassword123"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Add more tests as needed for your application
