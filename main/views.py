# from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.cache import cache

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


class Notification_service:
    @staticmethod
    def send_notification(text,type, email):
        request_data = {
            "text": text,
            "type": type,
            "email_send": "True",
            "email": email
        }
        notification_service_url = settings.NOTIFICATION_SERVICE_URL + "/main/add/"  
        response = requests.post(notification_service_url, json=request_data)
        response.raise_for_status()
        # return True
# account_enter
# email_code
# task_time
# user_add_task


class Email_service:
    @staticmethod
    def send_code(email):
        code = str(random.randint(100000, 999999)) # добавить проверку на уникальность
        cache.set(f"email_code:{email}", code, timeout=300)
        Notification_service.send_notification(f"код для авторизации PlanIT: {code}", "email_code", email)

    @staticmethod
    def verefy_email(email, code):
        saved_code = cache.get(f"email_code:{email}")
        if not saved_code:
            raise Exception(f"Code expired or invalid")

        if saved_code != code:
            raise Exception(f"Invalid code")
        return email
    

class User_service:
    @staticmethod
    def autenticate(email, code):
        Email_service.verefy_email(email, code)
        user = User.objects.get(email=email)
        tokens = RefreshToken.for_user(user)
        Notification_service.send_notification(f"В ваш аккаунт PlanIT был осуществлен вход", "account_enter", email)
        return {
            "access": str(tokens.access_token),
            "refresh": str(tokens),
        }
    @staticmethod
    def register(data):
        serializer = UserSerializer(data = data)
        Email_service.verefy_email(data['email'], data['code'])
        if serializer.is_valid():
            user = serializer.save() 
            user.refresh_from_db()
            tokens = RefreshToken.for_user(user)
            Notification_service.send_notification(f"Добро пожаловать в PlanIT", "account_enter", data['email'])
            return {
                "access": str(tokens.access_token),
                "refresh": str(tokens),
            }
        raise Exception(f"Invalid data for user serializer")

    
class UserAction(viewsets.ViewSet):
    def send_email_code(self, request):
        try:
            Email_service.send_code(request.data.get('email'))
            return Response({"messege": "sucsess"}, status=203)
        except Exception as e:
            return Response(f"error: {e}", status=status.HTTP_400_BAD_REQUEST)
    def autenticate(self, request):
        try:
            tokens = User_service.autenticate(request.data.get('email'), request.data.get('code'))
            return Response(tokens, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(f"error: {e}", status=status.HTTP_400_BAD_REQUEST)
    def register(self, request):
        try:
            tokens = User_service.autenticate(request.data.get('email'), request.data.get('code'))
            return Response(tokens, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(f"error: {e}", status=status.HTTP_400_BAD_REQUEST)
            

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