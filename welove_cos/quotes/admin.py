from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Quote, Source, Profile


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('source', 'quote_text')
    list_filter = ['source']
    search_fields = ['source', 'quote_text']


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    list_filter = ['name']
    search_fields = ['name']


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profile"


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )


admin.site.register(Quote, QuoteAdmin)
admin.site.register(Source, SourceAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
