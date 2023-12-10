from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

"""Testing: a separate note is transferred to the
page with notes list in the 'object_list' of the 'content'.
"""


class TestContent(TestCase):
    """Тестирование: на страницы создания
    и редактирования заметки передаются формы.
    """

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.create = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='my-slug',
            author=cls.author,
        )

    def test_note_in_list_of_different_users():
        """Тестирование: в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        user_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            with self.subTest(user=user):
                url = reverse('notes:list')
                response = self.client.get('url')
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), status)

    def test_anonymous_client_has_no_form(self):
        urls = (
            ('notes:edit'),
            ('notes:add'),
        )
        for name in urls:
            with self.subTest(name=name):
                if name == 'notes:add':
                    url = reverse(name)
                else:
                    url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        user = self.author
        self.client.force_login(user)
        urls = (
            ('notes:edit'),
            ('notes:add'),
        )
        for name in urls:
            with self.subtest(name=name):
                if name == 'notes:add':
                    url = reverse(name)
                else:
                    url = reverse(name, args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)
