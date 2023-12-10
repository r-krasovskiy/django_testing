import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
def test_comments_order(client):
    """Тестирование: новости отсортированы от самой свежей
    к самой старой; свежие новости в начале списка.
    """
    response = client.get(detail_url)
    assert 'news' in response.context

    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_comments = sorted(all_dates)
    assert all_comments == sorted_comments




"""Тестирование: анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна."""
