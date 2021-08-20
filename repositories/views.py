from rest_framework import mixins, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Commit, Repository
from .serializers import CommitSerializer, RepositorySerializer
from .services import check_repo_exists_database, check_repo_exists_remote
from .tasks import save_last30days_commits


class CommitView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommitSerializer
    queryset = Commit.objects.all()


class RepositoryView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    def perform_create(self, serialiazer):
        validate = check_repo_exists_remote(
            self.request) and not check_repo_exists_database(self.request)
        if(validate):
            repo = serialiazer.save(user_id=self.request.user.id)
            save_last30days_commits.delay(
                self.request.data['name'], self.request.user.id)
            return Response(serialiazer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Not Found or Already on database.'}, status=status.HTTP_404_NOT_FOUND)
