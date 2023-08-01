from django.contrib import admin

from users.models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
