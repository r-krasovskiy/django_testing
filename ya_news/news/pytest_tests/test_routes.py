import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('urls_news_home'),
        pytest.lazy_fixture('urls_users_login'),
        pytest.lazy_fixture('urls_users_logout'),
        pytest.lazy_fixture('urls_users_signup'),
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, url):
    """Тест, пункты 1, 6:
    - главная страница доступна анонимному пользователю;
    - страницы регистрации пользователей, входа в учётную запись
     и выхода из неё доступны анонимным пользователям.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_availability_for_anonymous_user(client, urls_news_detail):
    """Тест, пункт 2: страница отдельной новости
    доступна анонимному пользователю.
    """
    response = client.get(urls_news_detail)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('urls_news_edit'),
        pytest.lazy_fixture('urls_news_delete')
    )
)
@pytest.mark.django_db
def test_pages_availability_for_different_users(
    parametrized_client, url, comment, expected_status
):
    """Тест, пункты 3, 5:
    - страницы удаления и редактирования комментария доступны
    автору комментария;
    - авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев (возвращается ошибка 404).
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('urls_news_edit'),
        pytest.lazy_fixture('urls_news_delete'),
    ),
)
@pytest.mark.django_db
def test_redirects(client, url, urls_users_login):
    """Тест, пункт 4: при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    expected_url = f'{urls_users_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
