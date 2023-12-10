from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.note = Note.objects.create(title='Заголовок', text='Текст')
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель заметки')


    """Testing availability of the main page for authonificated
    and non-authonificated users;
    testing of list of the notes, adding note and successful adding a new note
    are available for authonificated users.
    """
    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.id,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    """Testing of availability of a note editing and deletion
    for its author only.
    """
    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    """Testing redirects: non-authonificated users will be transferred
    to logg-in page if they try to get:
     - a successfull adding of a note;
     - a separate note;
     - editing or deletion of a note."""
    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.id,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
