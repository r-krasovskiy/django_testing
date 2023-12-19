import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse

from yanews import settings


@pytest.mark.django_db
def test_news_count(client, urls_news_home):
    """Тест, пункт 1: количество новостей
    на главной странице — не более 10.
    """
    response = client.get(urls_news_home)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_from_newest_to_oldest(client):
    """Тестирование, пункт 2: новости отсортированы от самой свежей
    к самой старой, свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_news = [news.date for news in object_list]
    news_sorted = sorted(all_news, reverse=True)
    assert news_sorted == all_news



@pytest.mark.django_db
@pytest.mark.usefixtures('all_comments')
def test_comments_order_from_newest_to_oldest(news, client):
    """Тестирование, пункт 3: комментарии на странице отдельной новости
    отсортированы в хронологическом порядке: старые в начале списка,
    новые — в конце.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']

    object_list = news.comment_set.all()
    all_comments = [comment.created for comment in object_list]
    sorted_comments = sorted(all_comments)
    assert sorted_comments == all_comments



"""Тестирование, пункт 4: анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна."""
@pytest.mark.parametrize(
    'parametrized_client, form',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_edit_comment_page_contains_form(id_for_args, parametrized_client, form):
    url = reverse('news:detail', args=id_for_args)
    response = parametrized_client.get(url)
    assert form in response.context
