from django.contrib.auth import get_user_model
from django.db import models


class Repository(models.Model):
    name = models.CharField(max_length=100)

    user = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Repositories'
        constraints = [models.UniqueConstraint(
            fields=['name'], name='repository_type_unq')]


class Commit(models.Model):
    message = models.TextField()
    sha = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    url = models.URLField(max_length=200)
    date = models.DateTimeField()
    avatar = models.URLField(max_length=200, blank=True)

    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('-date',)
