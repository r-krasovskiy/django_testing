from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Testing: only authonificated users can create notes."""

    NOTE_TEXT = 'Текст заметки.'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки.'

    @classmethod
    def setUpTestData(cls):
        cls.notes = Note.objects.create(title='Заголовок', text='Текст')
        cls.url = reverse('notes:detail', args=(cls.notes.id,))
        cls.user = User.objects.create(username='Пользователь 1')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.NOTE_TEXT}

    def test_anonymous_user_cant_create_notes(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{self.url}#notes')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.notes, self.notes)
        self.assertEqual(note.author, self.user)


"""Testing: creation of 2 notes with the same slug is impossible."""


"""Testing: if slug fild was not created within new note registration,
it will be created automatically from the title of the note.
"""


class TestCommentEditDelete(TestCase):
    """Testing: a user can create and edit own notes,
    but can't do these actions with others.
    """

    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.notes = Note.objects.create(title='Заголовок', text='Текст')
        note_url = reverse('notes:detail', args=(cls.notes.id,))
        cls.url_to_notes = note_url + '#notes'
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            notes=cls.note,
            author=cls.author,
            text=cls.NOTE_TEXT
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.id,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.id,))
        cls.form_data = {'text': cls.NOTE_TEXT}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_notes)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_notes)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_COMMENT_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
