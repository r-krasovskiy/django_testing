import pytest
# from datetime import timedelta
# from django.utils import timezone

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

"""
@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
"""
