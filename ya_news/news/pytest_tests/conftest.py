import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse

from yanews import settings
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура автора новости."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    """Фикстура залогиненного автора новости."""
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    """фикстура незалогиненного читателя."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, admin_client):
    """фикстура залогиненного читателя."""
    admin_client.force_login(reader)
    return admin_client


@pytest.fixture
def news():
    """фикстура новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(author, news):
    """Фикстура комментария к новости."""
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def urls_news_home():
    return reverse('news:home')


@pytest.fixture
def urls_users_login():
    return reverse('users:login')


@pytest.fixture
def urls_users_logout():
    return reverse('users:logout')


@pytest.fixture
def urls_users_signup():
    return reverse('users:signup')


@pytest.fixture
def urls_news_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def urls_news_edit(news):
    return reverse('news:edit', args=(news.id,))


@pytest.fixture
def urls_news_delete(comment):
    return reverse('news:delete', args=(comment.id,))
