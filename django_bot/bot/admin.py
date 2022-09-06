from django.contrib import admin
from .models import UserTg, RequestResponse, StandardMessages


class UserTGAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_id')
    search_fields = ('user_name', 'user_id')

class RequestResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'request', 'response')
    search_fields = ('user__user_name', )


admin.site.register(UserTg, UserTGAdmin)
admin.site.register(RequestResponse, RequestResponseAdmin)
admin.site.register(StandardMessages)
