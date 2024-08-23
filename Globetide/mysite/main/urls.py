from django.shortcuts import render
from django.urls import path, register_converter
from django.http import HttpResponse
from . import views
from django.contrib.auth import views as auth_views
from .converters import FloatConverter

register_converter(FloatConverter, 'float')


urlpatterns = [
    path('upload_sd/', views.upload_sd, name='upload_sd'),
    path('', views.sign_up, name="sign_up"),
    path('profile/', views.profile, name="profile"),
    path('login/', views.login1, name="login"),
    path('create-trip/', views.create_trip, name='create-trip'),
    path('home/', views.home, name='home'),
    path('otp/', views.verify, name="otp"),
    path('budget/', views.budget, name='budget'),
    path('delete_trip/<int:trip_id>/', views.delete_trip, name='delete_trip'),
    path('delete_shared_trip/<int:trip_id>/', views.delete_shared_trip, name='delete_shared_trip'),
    path('budget/<str:jwt_token>/', views.budget, name='budget'),
    path('reset_check_email/', views.reset_check_email, name='reset_check_email'),
    path('password_reset_sent/', views.password_reset_sent, name='password_reset_sent'),
    path('reset_user_password/<uid>/<token>/', views.reset_user_password, name='reset_user_password'),
    path('test/', views.test, name="test"),
    path('logindata/', views.logindata, name="calendar"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='main/password_reset.html'), name='reset_password'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/password_reset_form.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password_reset_done.html'), name='password_reset_complete'),
    #path('email/', views.email, name='email'),
    path('email/<str:trip_id>', views.email, name='email'),
    path('revised', views.revised, name='revised'),
    path('notifications/', views.notifications, name='notifications'),
    path('weather/<float:latitude>/<float:longitude>/', views.weather, name='weather'),
    path('blog/', views.blog_general, name="blog_general"),
    path('map/<float:latitude>/<float:longitude>', views.map_view, name='map_view'),
    path('blog/<str:category>/', views.blog, name='blog'),
    path('blog/<str:category>/<str:username>/<int:id>/', views.blog, name='blog'),
    path('create-blog', views.create_blog, name='create-blog'),
    path('translate/', views.translate, name='translate'),
    path('key/<str:param>', views.select_destination, name='select_destination'),
    path('cow/', views.cow, name='cow'),
    path('overview/', views.trip_overview, name='trip-overview'),
    path('checklist/', views.checklist, name='checklist'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('search/', views.search_bar, name='search_bar'),
    path('photos/', views.pexel, name='pexel')

]
