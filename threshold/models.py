from django.db import models

# Create your models here.

class Geopod(models.Model):
    name = models.CharField(max_length=128)
    subdomain = models.CharField(max_length=128)
    access_token = models.CharField(max_length=50)
    access_token_secret = models.CharField(max_length=50)
    
    