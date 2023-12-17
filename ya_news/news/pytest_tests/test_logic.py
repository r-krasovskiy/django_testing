import random
import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING



COMMENT_TEXT_NEW = 'Новый текст комментария.'

"""Тестирование, пункт 1: анонимный пользователь
не может отправить комментарий"""
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data):
    url = reverse('news: details')
    response = client.post(url, form=form_data)
    login_url = reverse('user:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count == 0







"""Тестирование, пункт 2: авторизованный пользователь
может отправить комментарий.
"""
def test_user_can_create_comment(author_client, author, form_data, news):
    url = reverse('news:detail')
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('news:success'))
    comment_count = Comment.objects.count()
    assert comment_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author_client


















def test_user_cant_use_bad_words(admin_client, news):
    """Тестирование, пункт 3: если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {
        'text': f'Текст комментария, {random.choice(BAD_WORDS)}, текст'
    }
    comment_count_before = Comment.objects.count()

    url = reverse('news:detail', args=(news.id,))
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)

    comment_count_after = Comment.objects.count()
    assert comment_count_before == comment_count_after


"""Тестирование, пункт 4: авторизованный пользователь может
редактировать или удалять свои комментарии.
"""

@pytest.mark.django_db
def test_user_can_edit_own_comments(author_client, id_for_args, comment):
    url = reverse('news:edit', args=id_for_args)
    # comment_old = comment.text
    form_data = {'text': 'Обновленный текст коментария.'}
    response = author_client.post(url, form_data)
    new_url = url + '#comments'
    comment.refresh_from_db()
    assertRedirects(response, new_url)
    assert comment == form_data['text']



"""Тестирование, пункт 5: авторизованный пользователь
не может редактировать или удалять чужие комментарии
"""
def test_user_cant_edit_comments_of_other_users(
        admin_client, id_for_args, comment
):
    url = reverse('news:edit', args=id_for_args)
    comment_old = comment.text
    form_data = {'text': 'Обновленный текст коментария.'}
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_old

@pytest.mark.django_db
def test_user_cant_delete_comments_of_other_users(
    admin_client, id_for_args
):
    url = reverse('news:delete', args=id_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    expected_comments_count = 1
    assert Comment.objects.count() == expected_comments_count


"""
@pytest.mark.django_db
def test_user_can_create_comment(author_client, form_data, detail_url, news):
    response = autor_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    coments_count = Comment.objects.get()
    assert comment.text == form.data['text']
    assert comment.news == news
    assert comment.author == author_client

@pytest.mark.django_db
def test_author_can_edit_comment(comment, detail_url, author_client):
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data ={'text': COMMENT_TEXT_NEW}
    response = author_client.post(edit_url, data=form_data)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment == COMMENT_TEXT_NEW
"""
