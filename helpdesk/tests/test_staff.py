from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client
from helpdesk.models import CustomField, Queue, Ticket

try:  # python 3
    from urllib.parse import urlparse
except ImportError:  # python 2
    from urlparse import urlparse

from helpdesk.templatetags.ticket_to_link import num_to_link
from helpdesk.views.staff import _is_my_ticket2


class StaffTestCase(TestCase):
    fixtures = ['emailtemplate.json']

    def setUp(self):
        self.queue_public = Queue.objects.create(
            title='Queue 1',
            slug='q1',
            allow_public_submission=True,
            new_ticket_cc='new.public@example.com',
            updated_ticket_cc='update.public@example.com'
        )

        self.ticket_data = {
            'title': 'Test Ticket',
            'description': 'Some Test Ticket',
        }

        self.client = Client()

    def loginUser(self, is_staff=True):
        """Create a staff user and login"""
        User = get_user_model()
        self.user = User.objects.create(
            username='User_1',
            is_staff=is_staff,
        )
        self.user.set_password('pass')
        self.user.save()
        self.client.login(username='User_1', password='pass')
        
    def test_is_my_ticket(self):
        """Tests whether non-staff but assigned user still counts as owner"""

        # make non-staff user
        self.loginUser(is_staff=False)

        # create second user
        User = get_user_model()
        self.user2 = User.objects.create(
            username='User_2',
            is_staff=False,
        )

        initial_data = {
            'title': 'Private ticket test',
            'queue': self.queue_public,
            'assigned_to': self.user,
            'status': Ticket.OPEN_STATUS,
        }

        # create ticket
        ticket = Ticket.objects.create(**initial_data)

        self.assertEqual(_is_my_ticket2(self.user, ticket), True)
        self.assertEqual(_is_my_ticket2(self.user2, ticket), False)

    def test_is_not_my_ticket(self):
        """Tests whether non-staff but assigned user still counts as owner"""

        # make non-staff user
        self.loginUser(is_staff=True)

        # create second user
        User = get_user_model()
        self.user2 = User.objects.create(
            username='User_3',
            is_staff=True,
        )

        initial_data = {
            'title': 'Private ticket test',
            'queue': self.queue_public,
            'assigned_to': self.user,
            'status': Ticket.OPEN_STATUS,
        }

        # create ticket
        ticket = Ticket.objects.create(**initial_data)

        self.assertEqual(_is_my_ticket2(self.user, ticket), True)
        self.assertEqual(_is_my_ticket2(self.user2, ticket), True)
