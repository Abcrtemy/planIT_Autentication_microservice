# from django.shortcuts import render
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from main.models import User
from django.contrib import auth
from .serializers import UserSerializer


class UserAction(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save() # вызывает метод create в сериализаторе автоматом)
            print("Перед сохранением:", user.password)
            user.refresh_from_db()
            tokens = RefreshToken.for_user(user)
            access_token = str(tokens.access_token)
            refresh_token = str(tokens)
            return Response(
                {
                    "message": "Пользователь успешно зарегистрирован",
                    "access": access_token,
                    "refresh": refresh_token
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateTokenView(APIView):
    permission_classes = [AllowAny]
    user = User.objects.get(login = 'ahrenella')
    print(user.id)
    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        
        if not token:
            return Response({"valid": False, "error": "Token not provided"}, status=402)
        
        try:
            access_token = AccessToken(token)
            return Response({"valid": True, "user_id": access_token["user_id"]})
        except Exception as e:
            return Response({"valid": False, "error": str(e)}, status=403)
        # return Response({"valid": False, "error": str(e)}, status=401)
        
