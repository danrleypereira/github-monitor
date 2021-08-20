from django.urls import path

from .views import CommitView, RepositoryView

app_name = 'repositories'

urlpatterns = [
    path('api/commits/', CommitView.as_view(), name='commits-list'),
    path('api/repositories/', RepositoryView.as_view(), name='repositories-create'),
]
