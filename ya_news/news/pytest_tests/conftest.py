from datetime import datetime, timedelta

from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура автора новости (первого юзера)."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Фикстура залогиненного автора новости (первого юзера)."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    """Фикстура незалогиненного читателя (второго юзера)."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, admin_client):
    """Фикстура залогиненного читателя (второго юзера)."""
    admin_client.force_login(reader)
    return admin_client


@pytest.fixture
def news():
    """Фикстура новости."""
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
def all_news():
    """Фикстура для проверки числа новостей наnews:home."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def all_comments(news, author):
    """Фикстура для проверки порядка показа комментариев"""
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


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
