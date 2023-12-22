from http import HTTPStatus

from django.contrib.auth import get_user, get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

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

        cls.URLS_NOTES_HOME = reverse('notes:home')
        cls.URLS_USERS_SIGNUP = reverse('users:signup')
        cls.URLS_USERS_LOGIN = reverse('users:login')
        cls.URLS_USERS_LOGOUT = reverse('users:logout')
        cls.URLS_NOTES_DETAIL = reverse('notes:detail', args=(cls.note.slug,))
        cls.URLS_NOTES_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.URLS_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URLS_NOTES_ADD = reverse('notes:add')
        cls.URLS_NOTES_LIST = reverse('notes:list')
        cls.URLS_NOTES_SUCCESS = reverse('notes:success')

    def test_pages_availability(self):
        """Тест, пункты 1, 5:
        - главная страница доступна анонимному пользователю;
        - страницы регистрации пользователей, входа в учётную запись
        и выхода из неё доступны всем пользователям.
        """
        urls = (
            self.URLS_NOTES_HOME,
            self.URLS_USERS_SIGNUP,
            self.URLS_USERS_LOGIN,
            self.URLS_USERS_LOGOUT
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Тест, пункт 2: аутентифицированному пользователю доступна
        страница со списком заметок notes/,
        страница успешного добавления заметки done/,
        страница добавления новой заметки add/.
        """
        urls = (
            self.URLS_NOTES_LIST,
            self.URLS_NOTES_SUCCESS,
            self.URLS_NOTES_ADD)
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_reader.get(url)
                self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Тест, пункт 3: страницы отдельной заметки, удаления
        и редактирования заметки доступны только автору заметки.
        Если на эти страницы попытается зайти
        другой пользователь— вернётся ошибка 404.
        """
        urls = (
            self.URLS_NOTES_DETAIL,
            self.URLS_NOTES_DELETE,
            self.URLS_NOTES_EDIT,
        )
        users_availability = (
            (self.auth_author, HTTPStatus.OK),
            (self.auth_reader, HTTPStatus.NOT_FOUND),
        )
        for user, result in users_availability:
            for url in urls:
                with self.subTest(url=url, result=result, user=get_user(user)):
                    response = user.get(url)
                    self.assertEqual(response.status_code, result)

    def test_redirects(self):
        """Тест, пункт 4: при попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления заметки,
        отдельной заметки, редактирования или удаления заметки анонимный
        пользователь перенаправляется на страницу логина.
        """
        urls = (
            self.URLS_NOTES_LIST,
            self.URLS_NOTES_SUCCESS,
            self.URLS_NOTES_ADD,
            self.URLS_NOTES_DETAIL,
            self.URLS_NOTES_EDIT,
            self.URLS_NOTES_DELETE,
        )
        for url in urls:
            with self.subTest(url=url):
                expected_url = f'{self.URLS_USERS_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
