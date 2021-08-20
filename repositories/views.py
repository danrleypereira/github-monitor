from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.views import APIView

from .models import Commit
from .serializers import CommitSerializer, RepositorySerializer
from .tasks import save_last30days_commits

from .services import check_repo_exists_remote, check_repo_exists_database

class CommitView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        commits = Commit.objects.all()
        serializer = CommitSerializer(commits, many=True)
        return Response(serializer.data)

class RepositoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        validate = check_repo_exists_remote(request) and not check_repo_exists_database(request)
        if(validate):
            serializer = RepositorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            save_last30days_commits.delay(request.data["name"], request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"Not Found or Already on database."}, status=status.HTTP_404_NOT_FOUND)
