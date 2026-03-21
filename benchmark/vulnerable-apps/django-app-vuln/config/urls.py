from django.urls import path
from app import views
urlpatterns = [
    path("", views.index),
    path("api/auth/register/", views.register),
    path("api/auth/login/", views.login),
    path("api/profile/<str:profile_id>/", views.get_profile),
    path("api/profile/", views.create_profile),
    path("api/profile/<str:profile_id>/update/", views.update_profile),
    path("api/search/", views.search),
    path("api/upload/", views.upload),
    path("api/file/", views.read_file),
    path("api/run/", views.run_cmd),
    path("api/admin/users/", views.admin_users),
    path("api/config/load/", views.config_load),
    path("api/eval/", views.do_eval),
    path("api/echo/", views.echo),
]
