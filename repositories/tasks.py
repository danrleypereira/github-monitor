from celery.utils.log import get_task_logger
from django.contrib.auth.models import User

from githubmonitor.celery import app
from repositories import serializers

from .models import Repository
from .services import get_last30days_commits, save_commits

logger = get_task_logger(__name__)


@app.task(bind=True, retry_limit=2, default_retry_delay=3, serializer='json')
def save_last30days_commits(self, repo, user_id):
    user = User.objects.get(id=user_id)
    try:
        repo = Repository.objects.get(name=repo)
    except Repository.DoesNotExist as e:
        logger.info('Repository does not exist: {0}'.format(repo))
        self.retry(exc=e)
    commits = get_last30days_commits(str(repo), user)

    try:
        save_commits(commits, repo)
        logger.info(
            'Commits from remote saved successfully: {0}'.format(commits))
    except Exception as e:
        self.retry(exc=e)
