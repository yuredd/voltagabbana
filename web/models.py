from django.contrib.auth.models import User
from django.db import models

class Politician(models.Model):
    present = models.BooleanField(default=False)
    area = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)
    gender = models.CharField(max_length=10,null=True)
    group = models.CharField(max_length=150)
    dateOfBirth = models.DateField(null=True)
    dateUpdate = models.DateField(null=True)
    placeOfBirth = models.CharField(max_length=150,null=True)
