import pytest
from datetime import datetime, timedelta
from django.utils import timezone

from yanews import settings
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """фикстура автора новости."""
    return django_user_model.objects.create(username='Автор')

@pytest.fixture
def author_client(author, client):
    """фикстура залогиненного автора новости."""
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    """фикстура незалогиненного читателя."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, client):
    """фикстура залогиненного читателя."""
    client.force_login(reader)
    return reader_client


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
def all_news():
    """Фикстура списка всех новостей в базе."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Текст новости.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def all_comments(news, author):
    """Фикстура списка всех комментариев в базе."""
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}',
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def id_for_args(comment):
    """Фикстура с id комментариев"""
    return comment.id,


@pytest.fixture
def updated_comment(author, news):
    """Фикстура редактирования комментария к новости."""
    comment = Comment.objects.create(
        news=news,
        text='Скорректированный текст комментария',
        author=author,
    )
    return comment
