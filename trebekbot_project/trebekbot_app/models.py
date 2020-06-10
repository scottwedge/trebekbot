from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)