from django.contrib.auth import get_user_model
from rest_framework import viewsets
from users.models import CustomUser
from users.serializers import (AvatarSerializer, UserSingupSerializer, UserSerializer)
from api.permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserSingupSerializer
    
class AvatarViewSet(viewsets.ModelViewSet):
    #search_fields = ('name',)
    #lookup_field = 'slug'
    queryset = CustomUser.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    http_method_names = ['put', 'delete']

    def get_paginated_response(self, data):
        return Response(data)