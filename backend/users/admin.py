from django.contrib import admin
from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка пользователей."""
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'role'
    )
    list_filter = ('email', 'username')
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка подписок."""
    list_display = ('user', 'author')
    empty_value_display = '-пусто-'
