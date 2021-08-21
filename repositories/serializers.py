from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Commit, Repository


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ('name',)
        extra_kwargs = {
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=Repository.objects.all(),
                        message=("Repository already exists in database")
                    )
                ]
            }
        }


class CommitSerializer(serializers.ModelSerializer):
    repository = serializers.StringRelatedField(many=False)

    class Meta:
        model = Commit
        fields = (
            'message',
            'sha',
            'author',
            'url',
            'avatar',
            'date',
            'repository',
        )

        read_only_fields = (
            'message',
            'sha',
            'author',
            'url',
            'avatar',
            'date',
            'repository',
        )
