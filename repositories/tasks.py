import requests as req
import json
from datetime import datetime, timedelta

from social_django.models import UserSocialAuth
from django.contrib.auth.models import User
from django.db import transaction

from githubmonitor.celery import app
from repositories import serializers
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from .models import Repository, Commit

@app.task(serializer='json')
def check_repo_exists_remote(ui_request):
    url_base = "https://api.github.com/repos/"
    owner = ui_request.user
    repo = ui_request.data["name"]
    url = url_base+ str(owner) +"/"+ str(repo)
    request_repo_git = req.get(url)
    if request_repo_git.status_code != 200:
        logger.info("Repository does not exist at remote: {0}".format(str(repo)))
        return False
    logger.info("Repository exist at remote: {0}".format(str(repo)))
    return True

@app.task(serializer='json')
def check_repo_exists_database(ui_request):
    repo = ui_request.data["name"]
    try:
        Repository.objects.get(name=str(repo))
    except Repository.DoesNotExist:
        return False
    return True

# @transaction.atomic()
@app.task(bind=True, retry_limit=2, default_retry_delay=3, serializer='json')
def save_last30days_commits(self, repo, user_id):
    user = User.objects.get(id= user_id)
    try:
        repo = Repository.objects.get(name=repo)
    except Repository.DoesNotExist as e:
        logger.info('Repository does not exist: {0}'.format(repo))
        self.retry(exc= e)
    commits = get_last30days_commits(str(repo), user)

    logger.info('Commits from remote: {0}'.format(commits))
    try:
        save_commits(commits, repo)
    except Exception as e:
        self.retry(exc= e)

@transaction.atomic()
def save_commits(commits, repo):
    try:
        for com in commits:
            serializer = Commit(
                message= com["commit"]["message"],
                sha= com["sha"],
                author= com["author"]["login"] if com['author'] else 'not defined',
                url= com["url"],
                date= com["commit"]["author"]["date"],
                avatar= com["author"]["avatar_url"] if com['author'] else 'https://avatars.githubusercontent.com/u/16515996',
                repository= repo
            )
            serializer.save()
    except Exception as e:
        raise e

@app.task(serializer='json')
def get_last30days_commits(repo, owner):
    url_base = "https://api.github.com/repos/"
    url = url_base + str(owner) +"/"+ repo +"/commits"
    today = datetime.today()
    payload = UserSocialAuth.objects.select_related("user").get(user_id=owner.id)
    access_token = payload.__dict__["extra_data"]["access_token"]
    token_type = payload.__dict__["extra_data"]["token_type"].capitalize()

    response_commits = req.get(url, params={ "since": today - timedelta(days=31)}, headers={
        "Authorization": token_type +" "+ access_token,
    })
    res = response_commits._content.decode("utf8")
    return json.loads(res)


@app.task(serializer='json')
def request_user_data(ui_request):
    url_base = "https://api.github.com/user"
    owner = ui_request.user
    url = url_base
    payload = UserSocialAuth.objects.select_related("user").get(user_id=owner.id)
    access_token = payload.__dict__["extra_data"]["access_token"]
    token_type = payload.__dict__["extra_data"]["token_type"].capitalize()
    response_user = req.get(url, params=None, headers={
        "Authorization": token_type +" "+ access_token,
    })
    res = response_user._content.decode("ascii")
    return json.loads(res)

@app.task(serializer='json')
def logging(msg):
    log = msg
    print("\n"+ len(str(log))*"=" + "\n" + str(log) + "\n"+ len(str(log))*"=" + "\n")
