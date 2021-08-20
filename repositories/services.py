import json
from datetime import datetime, timedelta

import requests as req
from django.db import transaction
from social_django.models import UserSocialAuth

from .models import Commit, Repository

URL_BASE = 'https://api.github.com'


def check_repo_exists_remote(ui_request):
    owner = ui_request.user
    repo = ui_request.data['name']
    url = '{0}/{1}/{2}/{3}'.format(URL_BASE, 'repos', str(owner), str(repo))
    request_repo_git = req.get(url)
    if request_repo_git.status_code != 200:
        return False
    return True


def check_repo_exists_database(ui_request):
    repo = ui_request.data['name']
    try:
        Repository.objects.get(name=str(repo))
    except Repository.DoesNotExist:
        return False
    return True


def get_last30days_commits(repo, owner):
    url = URL_BASE + '/repos/' + str(owner) + '/' + repo + '/commits'
    today = datetime.today()
    payload = UserSocialAuth.objects.select_related(
        'user').get(user_id=owner.id)
    access_token = payload.__dict__['extra_data']['access_token']
    token_type = payload.__dict__['extra_data']['token_type'].capitalize()

    response_commits = req.get(url, params={'since': today - timedelta(days=31)}, headers={
        'Authorization': token_type + ' ' + access_token,
    })
    res = response_commits._content.decode('utf8')
    return json.loads(res)


@transaction.atomic()
def save_commits(commits, repo):
    try:
        for com in commits:
            serializer = Commit(
                message=com['commit']['message'],
                sha=com['sha'],
                author=com['author']['login'] if com['author'] else 'not defined',
                url=com['url'],
                date=com['commit']['author']['date'],
                avatar=com['author']['avatar_url'] if com['author'] else 'https://avatars.githubusercontent.com/u/16515996',
                repository=repo
            )
            serializer.save()
    except Exception as e:
        raise e


def request_user_data(ui_request):
    owner = ui_request.user
    url = URL_BASE + '/user'
    payload = UserSocialAuth.objects.select_related(
        'user').get(user_id=owner.id)
    access_token = payload.__dict__['extra_data']['access_token']
    token_type = payload.__dict__['extra_data']['token_type'].capitalize()
    response_user = req.get(url, params=None, headers={
        'Authorization': token_type + ' ' + access_token,
    })
    res = response_user._content.decode('ascii')
    return json.loads(res)


def logging(msg):
    log = msg
    print('\n' + len(str(log))*'=' + '\n' +
          str(log) + '\n' + len(str(log))*'=' + '\n')
