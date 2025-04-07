from main import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from main.views import ValidateTokenView, UserAction

app_name = 'main'

urlpatterns = [
    # path('', UserAction.as_view(), name='auth'), #отображение
    path('register/', UserAction.as_view({'post': 'register'}), name='register'),
    # path('register/', UserAction.as_view({'post': 'register'}), name='register'),
    path('get_email/', UserAction.as_view({'post': 'get_email'}), name='get_email'),
    path('send_email_code/', UserAction.as_view({'post': 'send_email_code'}), name='send_email_code'),
    # path('verefy_email_code/', UserAction.as_view({'post': 'verefy_email_code'}), name='verefy_email_code'),

    # path('token/', UserAction.autenticate(), name='tokenObtain'), #авторизация
    path('token/', UserAction.as_view({'post': 'autenticate'}), name='autenticate'),
    path('token/refresh/', TokenRefreshView.as_view(), name='tokenRefresh'), #продление токена

    path('validate/', ValidateTokenView.as_view(), name='tokenValidate')
    # path('task/update/', views.taskUpdate, name='taskUpdate'),
]