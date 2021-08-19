from os import access
import requests as req
import json
from datetime import datetime, timedelta
from githubmonitor.celery import app
from social_django.models import UserSocialAuth
# from django.contrib.auth.models import User

from .models import Repository

@app.task(serializer='json')
def check_repo_exists_remote(ui_request):
    url_base = "https://api.github.com/repos/"
    owner = ui_request.user
    repo = ui_request.data["name"]
    url = url_base+ str(owner) +"/"+ str(repo)
    request_repo_git = req.get(url)
    if request_repo_git.status_code != 200:
        return False
    return True 

@app.task(serializer='json')
def check_repo_exists_database(ui_request):
    repo = ui_request.data["name"]
    try:
        Repository.objects.get(name=str(repo))
    except Repository.DoesNotExist:
        return False
    return True

@app.task(serializer='json')
def get_last30days_commits(ui_request):
    repo = ui_request.data["name"]
    try:
        repo = Repository.objects.get(name=str(repo))
    except Repository.DoesNotExist:
        return
    url_base = "https://api.github.com/repos/"
    owner = ui_request.user
    url = url_base + str(owner) +"/"+ str(repo.name) +"/commits"
    today = datetime.today()
    payload = UserSocialAuth.objects.select_related("user").get(user_id=owner.id)
    access_token = payload.__dict__["extra_data"]["access_token"]
    token_type = payload.__dict__["extra_data"]["token_type"].capitalize()

    response_commits = req.get(url, params={ "since": today - timedelta(days=31)}, headers={
        "Authorization": token_type +" "+ access_token,
    })
    res = response_commits._content.decode("ascii")
    logging(res)
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