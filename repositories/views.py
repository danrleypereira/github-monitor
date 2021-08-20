from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Commit
from .serializers import CommitSerializer, RepositorySerializer
from .tasks import *

from .services import check_repo_exists_remote, check_repo_exists_database


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def commit_list_view(request):
    commits = Commit.objects.all()
    serializer = CommitSerializer(commits, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def repository_create_view(request):
    validate = check_repo_exists_remote(request) and not check_repo_exists_database(request)
    if(validate):
        serializer = RepositorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        save_last30days_commits.delay(request.data["name"], request.user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"message":"Not Found or Already on database."}, status=status.HTTP_404_NOT_FOUND)

