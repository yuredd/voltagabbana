from django.contrib import admin
from .models import Politician


class PoliticianAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name', 'area', 'gender', 'group', 'dateOfBirth', 'placeOfBirth', 'dateUpdate')

# Register your models here.
admin.site.register(Politician, PoliticianAdmin)
