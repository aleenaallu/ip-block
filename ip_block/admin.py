from django.contrib import admin

# Register your models here.
from .models import *
from django.apps import apps

apps = apps.get_app_config('ip_block')

for model_name, model in apps.models.items():
    admin.site.register(model)