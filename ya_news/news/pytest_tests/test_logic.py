import random
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_TEXT_UPD = 'Новый текст комментария.'


def test_anonymous_user_cant_create_comment(client, urls_news_detail):
    """Тест, пункт 1: анонимный пользователь не может отправить комментарий."""
    comments_before = Comment.objects.count()
    client.post(urls_news_detail, data={'text': COMMENT_TEXT_UPD})
    assert Comment.objects.count() == comments_before


def test_user_can_create_comment(
        author_client, urls_news_detail, news, author
):
    """Тест, пункт 2: авторизованный пользователь
    может отправить комментарий.
    """
    comments_before = Comment.objects.count()
    response = author_client.post(
        urls_news_detail, data={'text': COMMENT_TEXT_UPD}
    )
    assertRedirects(response, f'{urls_news_detail}#comments')
    assert Comment.objects.count() == comments_before + 1
    comment_new = Comment.objects.get()
    assert comment_new.text == COMMENT_TEXT_UPD
    assert comment_new.news == news
    assert comment_new.author == author


def test_user_cant_use_bad_words(author_client, urls_news_detail):
    """Тест, пункт 3: если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {
        'text': f'Текст комментария, {random.choice(BAD_WORDS)}, текст'
    }
    comments_before = Comment.objects.count()
    response = author_client.post(urls_news_detail, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == comments_before


def test_user_can_edit_own_comments(
    author_client, urls_news_edit, urls_news_detail, comment
):
    """Тест, пункт 4.1: авторизованный пользователь может
    редактировать свои комментарии.
    """
    author_id_old = comment.author_id
    news_id_old = comment.news_id
    response = author_client.post(
        urls_news_edit,
        data={'text': COMMENT_TEXT_UPD}
    )
    assertRedirects(response, f'{urls_news_detail}#comments')
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT_UPD
    assert comment.author_id == author_id_old
    assert comment.news_id == news_id_old


def test_user_can_delete_own_comments(
        author_client, urls_news_delete, urls_news_detail
):
    """Тест, пункт 4.2: авторизованный пользователь может
    удалять свои комментарии.
    """
    comments_before = Comment.objects.count()
    response = author_client.delete(urls_news_delete)
    assertRedirects(response, f'{urls_news_detail}#comments')
    assert Comment.objects.count() == comments_before - 1


def test_user_cant_edit_comments_of_other_users(
        reader_client, urls_news_edit, comment
):
    """Тест, пункт 5.1: авторизованный пользователь
    не может редактировать чужие комментарии.
    """
    comment_text_old = comment.text
    author_id_old = comment.author_id
    news_id_old = comment.news_id
    response = reader_client.post(
        urls_news_edit,
        data={'text': COMMENT_TEXT_UPD}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text_old
    assert comment.author_id == author_id_old
    assert comment.news_id == news_id_old


def test_user_cant_delete_comments_of_other_users(
    reader_client, urls_news_delete
):
    """Тест, пункт 5.2: авторизованный пользователь
    не может удалять чужие комментарии.
    """
    comments_before = Comment.objects.count()
    response = reader_client.delete(urls_news_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
