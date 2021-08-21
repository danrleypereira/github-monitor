from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Commit
from .serializers import CommitSerializer, RepositorySerializer
from .services import repo_exists_in_github
from .tasks import save_last30days_commits


class CommitView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommitSerializer
    queryset = Commit.objects.all()


class RepositoryView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RepositorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validate = repo_exists_in_github(
            self.request) and serializer.is_valid(raise_exception=True)
        if(validate):
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Not Found in GitHub'}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)
        save_last30days_commits.delay(
            self.request.data['name'], self.request.user.id)
