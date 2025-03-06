from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['login', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            login = validated_data['login'],
            password = validated_data['password'],
        )
        # user.set_password(validated_data['password'])  # Хешируем пароль!
        user.save()
        return user