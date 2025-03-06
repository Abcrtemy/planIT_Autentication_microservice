from main import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from main.views import ValidateTokenView, UserAction

app_name = 'main'

urlpatterns = [
    # path('', UserAction.as_view(), name='auth'), #отображение
    path('register/', UserAction.as_view(), name='tokenObtain'),

    path('token/', TokenObtainPairView.as_view(), name='tokenObtain'), #авторизация
    path('token/refresh/', TokenRefreshView.as_view(), name='tokenRefresh'), #авторизация

    path('validate/', ValidateTokenView.as_view(), name='tokenValidate')
    # path('task/update/', views.taskUpdate, name='taskUpdate'),
]