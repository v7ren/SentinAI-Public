from django.db import models
class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    role = models.CharField(max_length=20, default="user")
    class Meta:
        app_label = "app"

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    class Meta:
        app_label = "app"
