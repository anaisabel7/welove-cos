from django.contrib import admin

# Register your models here.

from .models import Quote, Source


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('source', 'quote_text')
    list_filter = ['source']
    search_fields = ['source', 'quote_text']


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    list_filter = ['name']
    search_fields = ['name']


admin.site.register(Quote, QuoteAdmin)
admin.site.register(Source, SourceAdmin)
