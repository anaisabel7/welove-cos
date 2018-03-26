from django.contrib import admin

# Register your models here.

from .models import Quote


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('source', 'quote_text')
    list_filter = ['source']
    search_fields = ['source', 'quote_text']


admin.site.register(Quote, QuoteAdmin)
