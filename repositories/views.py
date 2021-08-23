from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Commit, Repository
from .serializers import CommitSerializer, RepositorySerializer
from .services import repo_exists_in_github
from .tasks import save_last30days_commits


class CommitView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommitSerializer
    filter_backends = []
    filterset_fields = ('author',)

    def get_queryset(self):
        query_params = self.request.query_params
        author = query_params.get('author')
        repository = query_params.get('repository')
        repository_name = Repository.objects.get(name=repository)
        commits = Commit.objects.filter(author=author).filter(
            repository=repository_name.id)
        return commits


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
