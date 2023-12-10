import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from django.urls import reverse

from news.models import News, Comment


COMMENT_TEXT_NEW = 'Новый текст комментария.'














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

#def user_cant_edit_comment_of_another_user()
