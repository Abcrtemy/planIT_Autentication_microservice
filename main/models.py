from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


# class UserManager_(BaseUserManager):
#     def create_user(self, login, password, **extra_fields):
#         if not login:
#             raise ValueError("Логин обязателен")
#         user = self.model(login=login,login=login **extra_fields)
#         user.set_password(password)  # Хешируем пароль
#         return user
    
#     def create_superuser(self, login, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(login, password, **extra_fields)
class UserManager_(BaseUserManager):
    def create_user(self, login, email, **extra_fields):
        if not login:
            raise ValueError("Логин обязателен")
        user = self.model(login=login,email=email, **extra_fields)
        # user.set_password(password)  # Хешируем пароль
        return user
    
    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(login, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    # id = models.AutoField(primary_key=True)
    # team_id = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    login = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True) 
    class Roles(models.TextChoices):
        Po = 'po'
        developer = 'developer'
        tester = 'tester'
    role = models.CharField(max_length=20, choices=Roles.choices, default='developer')
    email = models.CharField(max_length=128, null=True, blank=True, unique=True)

    objects = UserManager_()
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False)  
    USERNAME_FIELD = 'login'  
    REQUIRED_FIELDS = [] 
    def __str__(self):
        return self.login


