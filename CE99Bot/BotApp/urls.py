from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('static_data_import_db/', static_data_import_db, name='static_data_import_db'),
    path('crawl_users_info/', crawl_users_info, name='crawl_users_info'),
    path('crawl_teachers_info/', crawl_teachers_info, name='crawl_teachers_info'),
    path('start_bot/<int:chat_id>/<str:username>/', start_bot, name='start_bot'),
    path('initial_create_user/<int:chat_id>/<str:username>/', initial_create_user, name='initial_create_user'),
    path('get_userpass/<int:chat_id>/<str:lms_username>/<str:lms_password>/', get_userpass, name='get_userpass'),
    path('show_main_table/<int:chat_id>/', show_main_table, name='show_main_table'),
    path('create_usercourse_cube/', create_usercourse_cube, name='create_usercourse_cube'),
]
