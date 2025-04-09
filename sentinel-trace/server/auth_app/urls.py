from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    CACLoginView,
    UserLogoutView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('login/cac/', CACLoginView.as_view(), name='cac-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
]
