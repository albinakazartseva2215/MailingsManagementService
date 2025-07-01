from django.contrib.auth.views import LoginView
from django.urls import path

from users.apps import UsersConfig
from users.views import UserCreateView, email_verification, ProfileDetailView, ProfileUpdateView, \
    user_logout, PasswordResetRequestView, PasswordResetConfirmView, UserListView, BlockUserView

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path('logout/', user_logout, name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('email-confirm/<str:token>/', email_verification, name='email-confirm'),
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/<int:pk>', ProfileUpdateView.as_view(), name='profile_edit'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('user/block/<int:pk>/', BlockUserView.as_view(), name='block_user'),
]
