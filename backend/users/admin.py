from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription

User = get_user_model()

admin.site.empty_value_display = 'Ещё ничего не задано'


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'username',
    )
    search_fields = (
        'email',
        'username',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'author',
        'subscriber',
    )
    list_filter = ('author',)
    search_fields = ('author',)
