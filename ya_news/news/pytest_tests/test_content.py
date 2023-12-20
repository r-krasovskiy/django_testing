import pytest

from yanews import settings


@pytest.mark.django_db
def test_news_count(client, urls_news_home, all_news):
    """Тест, пункт 1: количество новостей
    на главной странице — не более 10.
    """
    response = client.get(urls_news_home)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, urls_news_home):
    """Тест, пункт 2: новости отсортированы от самой свежей
    к самой старой, свежие новости в начале списка.
    """
    response = client.get(urls_news_home)
    object_list = response.context['object_list']
    all_news = [news.date for news in object_list]
    news_sorted = sorted(all_news, reverse=True)
    assert news_sorted == all_news


@pytest.mark.django_db
def test_comments_order(client, urls_news_detail, news):
    """Тест, пункт 3: комментарии на странице отдельной новости
    отсортированы в хронологическом порядке: старые в начале списка,
    новые — в конце.
    """
    response = client.get(urls_news_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_comments = [comment.created for comment in all_comments]
    sorted_comments = sorted(all_comments)
    assert sorted_comments == all_comments


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, urls_news_detail):
    """Тест, пункт 4.1: анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = client.get(urls_news_detail)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, urls_news_detail):
    """Тест, пункт 4.2: авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости.
    """
    response = author_client.get(urls_news_detail)
    assert 'form' in response.context
