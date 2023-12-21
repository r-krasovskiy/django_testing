from django.contrib.auth import get_user_model, get_user
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Подготовка фикстур для тестов.

        Args:
         reader: залогиненный юзер, читатель чужих заметок.
         author: залогиненный юзер, автор заметок.
         note: заметка.
        """
        cls.reader = User.objects.create(username='Читатель')
        cls.author = User.objects.create(username='Автор')
        cls.auth_reader = Client()
        cls.auth_author = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.auth_author.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_note_in_object_list(self):
        """Тест, пункт 1, 2:
        - отдельная заметка передаётся на страницу
        со списком заметок в списке object_list в словаре context;
        - в список заметок одного пользователя не попадают заметки
        другого пользователя.
        """
        users_availability = (
            (self.auth_author, True),
            (self.auth_reader, False),
        )
        for user, result in users_availability:
            with self.subTest(user=get_user(user), result=result):
                response = user.get(reverse('notes:list'))
                object_context = response.context['object_list']
                self.assertIs((self.note in object_context), result)

    def test_creation_and_edition_forms(self):
        """Тест, пункт 3: на страницы создания и редактирования
        заметки передаются формы.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for url, args in urls:
            with self.subTest(url=url):
                response = self.auth_author.get(reverse(url, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm,
                    msg=None)
