from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('urls_news_home'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),

        (pytest.lazy_fixture('urls_news_detail'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),

        (pytest.lazy_fixture('urls_news_edit'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('urls_news_delete'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('urls_news_edit'),

         pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('urls_news_delete'),
         pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),

        (pytest.lazy_fixture('urls_users_login'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('urls_users_login'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('urls_users_signup'),
         pytest.lazy_fixture('client'), HTTPStatus.OK)
    ),
)
def test_pages_availability(
    url, parametrized_client, expected_status, comment
):
    """Тест, пункты 1, 2, 3, 5, 6:
    - главная страница доступна анонимному пользователю;
    - страница отдельной новости доступна анонимному пользователю;
    - страницы удаления и редактирования комментария доступны
    автору комментария;
    - авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев (возвращается ошибка 404);
    - страницы регистрации пользователей, входа в учётную запись
     и выхода из неё доступны анонимным пользователям.
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
def test_redirects(client, url, urls_users_login):
    """Тест, пункт 4: при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    expected_url = f'{urls_users_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
