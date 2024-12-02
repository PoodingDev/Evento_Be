from drf_spectacular.utils import extend_schema
from jsonschema.validators import extend
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer, UserUpdateSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["사용자"])
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user_id": user.user_id,
                    "email": user.email,
                    "username": user.username,
                    "birth": user.birth,
                    "nickname": user.nickname,
                },
                status=201,
            )
        return Response(serializer.errors, status=400)


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["사용자"])
    def get_object(self):
        return self.request.user

    @extend_schema(tags=["사용자"])
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(tags=["사용자"])
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(tags=["사용자"])
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=204)
