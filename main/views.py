# from django.shortcuts import render
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import random
from django.core.cache import cache

from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
import requests

from main.models import User
from django.contrib import auth
from .serializers import UserSerializer

from django.conf import settings


class UserAction(viewsets.ViewSet):
    def send_email_code(self, request):
        email = request.data.get('email')
        code = str(random.randint(100000, 999999))
        cache.set(f"email_code:{email}", code, timeout=300)
        request_data = {
            "text": f"код для авторизации PlanIT: {code}",
            "type": "email_code",
            "email_send": "True",
            "email": email
        }
        try:
            notification_service_url = settings.NOTIFICATION_SERVICE_URL + "/main/add/"  
            response = requests.post(notification_service_url, json=request_data)
            response.raise_for_status()
            return Response({"messege": "sucsess"}, status=203)
        except requests.RequestException as e:
            print(f"Ошибка при отправке запроса в микросервис: {e}")
            return Response({"messege": {e}}, status=403)
        
    def verefy_email_code(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "Email and code are required"}, status=400)
        saved_code = cache.get(f"email_code:{email}")

        if not saved_code:
            return Response({"error": "Code expired or invalid"}, status=400)

        if saved_code != code:
            return Response({"error": "Invalid code"}, status=400)
        return Response({"messege": "code is ok"}, status=200)
        
            

    def register(self, request):
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
    def get_email(self, request):
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(id = user_id)
            if user.email:
                return Response({"messege": "sucsess", "email": user.email}, status=202)
            else:
                raise KeyError("User has no email")
        except Exception as e:
            return Response({"messege": str(e)}, status=403)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200: 
            tokens = response.data

            access_token = AccessToken(tokens["access"]) 
            user_id = access_token["user_id"]
            request_data = {
                "text": "В ваш аккаунт PlanIT был осуществлен вход",
                "type": "account_enter",
                "user_id": user_id,
                "email_send": "True"
            }

            try:
                notification_service_url = settings.NOTIFICATION_SERVICE_URL + "/main/add/"  
                requests.post(notification_service_url, json=request_data)
            except requests.RequestException as e:
                print(f"Ошибка при отправке запроса в микросервис: {e}")
        return response


class ValidateTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        if not token:
            return Response({"valid": False, "error": "Token not provided"}, status=402)
        
        try:
            access_token = AccessToken(token)
            # print(access_token["user_id"])
            response_data = ResponseCollector.collect(request, access_token["user_id"])
            return Response(response_data)
        except Exception as e:
            return Response({"valid": False, "error": str(e)}, status=403)
        # return Response({"valid": False, "error": str(e)}, status=401)
        
class ResponseCollector():
    def collect(request, user_id):
        user = User.objects.get(id = user_id)
        # print(user)
        response_data = {"valid": True, "user_id": user.id}
        # print(response_data)
        email = request.data.get("email")
        if email:
            response_data["email"] = user.email
        return response_data