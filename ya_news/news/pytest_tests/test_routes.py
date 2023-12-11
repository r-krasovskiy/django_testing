import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.urls import reverse

from news.models import News, Comment


COMMENT_TEXT = 'Текст комментария.'
COMMENT_TEXT_NEW = 'Новый текст комментария.'

@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    """Тестирование, пункт 1: главная страница
    доступна анонимному пользователю.
    """
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:detail', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Тестирование, пункт 2, 6: страница отдельной новости доступна анонимному
    пользователю; страницы регистрации пользователей, входа
    в учётную запись и выхода из неё доступны анонимным пользователям.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:detail', 'news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """Тестирование, пункты 3, 5: cтраницы удаления и редактирования
    комментария доступны автору комментария; при попытке перейти на
    страницу редактирования или удаления комментария анонимный
    пользователь перенаправляется на страницу авторизации.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, comment_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    ),
)
def test_redirects(client, name, comment_object):
    """Тестирование, пункт 4: при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_object.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
