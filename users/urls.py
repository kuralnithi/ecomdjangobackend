from django.urls import path
from . import views

urlpatterns = [
    path('user/register', views.register_user, name='register_user'),
    path('user/login', views.login_user, name='login_user'),
    path('getuser/', views.get_user_by_id, name='get_user_by_id'),
    path('resetpassword', views.reset_password, name='reset_password'),
    path('resetpasswordpage', views.reset_password_page, name='reset_password_page'),
    path('oauth', views.oauth_user, name='oauth_user'),
    path('verifytoken/', views.verify_token, name='verify_token'),
]