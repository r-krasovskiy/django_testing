from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):

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
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'new-slug'
        }

        cls.URLS_NOTES_ADD = reverse('notes:add')
        cls.URLS_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URLS_NOTES_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.URLS_NOTES_SUCCESS = reverse('notes:success')
        cls.NOTES_BEFORE = Note.objects.count()

    def test_user_can_create_note(self):
        """Тест, пункт 1.1: залогиненный пользователь может создать заметку."""
        response = self.auth_author.post(
            self.URLS_NOTES_ADD,
            data=self.form_data)
        self.assertRedirects(response, self.URLS_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE + 1)
        last_note = Note.objects.order_by('id').last()
        self.assertEqual(last_note.title, self.form_data['title'])
        self.assertEqual(last_note.text, self.form_data['text'])
        self.assertEqual(last_note.slug, self.form_data['slug'])
        self.assertEqual(last_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Тест, пункт 1.2: анонимный пользователь не может создать заметку."""
        self.client.post(self.URLS_NOTES_ADD, data=self.form_data)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE)

    def test_slug_is_unique(self):
        """Тест, пункт 2: невозможно создать две заметки с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        response = self.auth_author.post(
            self.URLS_NOTES_ADD,
            data=self.form_data
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE)

    def test_slug_is_empty(self):
        """Тест, пункт 3: Если при создании заметки не заполнен slug,
        то он формируется автоматически, с помощью функции
        pytils.translit.slugify.
        """
        self.form_data.pop('slug')
        response = self.auth_author.post(
            self.URLS_NOTES_ADD,
            data=self.form_data
        )
        self.assertRedirects(response, self.URLS_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE + 1)
        last_note = Note.objects.order_by('id').last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(last_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Тест, пункт 4.1: Пользователь может редактировать свои заметки."""
        response = self.auth_author.post(
            self.URLS_NOTES_EDIT,
            data=self.form_data
        )
        self.assertRedirects(response, self.URLS_NOTES_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE)
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        """Тест, пункт 4.2: Пользователь может удалять свои заметки."""
        response = self.auth_author.post(
            self.URLS_NOTES_DELETE,
            data=self.form_data
        )
        self.assertRedirects(response, self.URLS_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE - 1)

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест, пункт 4.3: Пользователь не может
        редактировать чужие заметки.
        """
        response = self.auth_reader.post(
            self.URLS_NOTES_EDIT,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_user_cant_delete_comment_of_another_user(self):
        """Тест, пункт 4.4: Пользователь не может удалять чужие заметки."""
        response = self.auth_reader.post(
            self.URLS_NOTES_DELETE,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE)
