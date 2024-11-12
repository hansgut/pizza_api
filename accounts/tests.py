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

    def test_address_creation(self):
        """
        Test that an authenticated user can create an address.
        """
        # Register and log in the user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Prepare address creation data
        address_data = {
            "street": "123 Main St",
            "city": "Springfield",
            "zip_code": "12345",
            "is_default": True,
            "address_type": "Home"
        }

        # Create the address
        response = self.client.post(reverse('user-address'), address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomerProfile.objects.filter(user__username='testuser').exists())
        self.assertTrue(CustomerProfile.objects.filter(user__username='testuser').exists())

    def test_get_addresses(self):
        """
        Test that an authenticated user can retrieve their addresses.
        """
        # Register and log in the user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Retrieve the addresses
        response = self.client.get(reverse('user-address'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_update_address(self):
        """
        Test that an authenticated user can update their address.
        """
        # Register and log in the user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Create an address
        address_data = {
            "street": "123 Main St",
            "city": "Springfield",
            "zip_code": "12345",
            "is_default": True,
            "address_type": "Home"
        }
        response = self.client.post(reverse('user-address'), address_data, format='json')
        address_id = response.data['id']

        # Prepare address update data
        update_data = {
            "street": "456 Elm St",
            "city": "Rivertown",
            "zip_code": "54321",
            "is_default": False,
            "address_type": "Work"
        }

        # Update the address
        response = self.client.put(reverse('user-address-detail', args=[address_id]), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the changes
        self.assertEqual(response.data['street'], '456 Elm St')
        self.assertEqual(response.data['city'], 'Rivertown')
        self.assertEqual(response.data['zip_code'], '54321')
        self.assertFalse(response.data['is_default'])
        self.assertEqual(response.data['address_type'], 'Work')

    def test_delete_address(self):
        """
        Test that an authenticated user can delete their address.
        """
        # Register and log in the user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Create an address
        address_data = {
            "street": "123 Main St",
            "city": "Springfield",
            "zip_code": "12345",
            "is_default": True,
            "address_type": "Home"
        }
        response = self.client.post(reverse('user-address'), address_data, format='json')
        address_id = response.data['id']

        # Delete the address
        response = self.client.delete(reverse('user-address-detail', args=[address_id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the address is deleted
        response = self.client.get(reverse('user-address'), format='json')
        self.assertEqual(len(response.data), 0)


    def test_get_foreign_addresses(self):
        """
        Test that an authenticated user cannot retrieve another user's addresses.
        """
        # Register and log in the first user
        self.client.post(self.registration_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Create an address for the first user
        address_data = {
            "street": "123 Main St",
            "city": "Springfield",
            "zip_code": "12345",
            "is_default": True,
            "address_type": "Home"
        }
        self.client.post(reverse('user-address'), address_data, format='json')

        # Register and log in the second user
        self.client.post(self.registration_url, {
            "username": "anotheruser",
            "email": "t@t.com",
            "password": "testpassword123",
            "profile": {
                "phone_number": "1234567890",
                "date_of_birth": "1990-01-01"
            }
        }, format='json')
        response = self.client.post(self.login_url, {
            "username": "anotheruser",
            "password": "testpassword123"
        }, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Attempt to retrieve the first user's addresses
        response = self.client.get(reverse('user-address'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertNotIn('123 Main St', response.data)
