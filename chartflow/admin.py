from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.
admin.site.register(
    models.Artist,
    search_fields = ("name",)
)
admin.site.register(models.Chart)
admin.site.register(models.ChartEntry)
admin.site.register(models.Country)
admin.site.register(models.CountryCluster)
admin.site.register(
    models.User, 
    UserAdmin, 
    list_display = ('username', 'email', 'role', 'is_staff'), 
    fieldsets = BaseUserAdmin.fieldsets + (('Additional Info', {'fields': ('role',)}),)
)
