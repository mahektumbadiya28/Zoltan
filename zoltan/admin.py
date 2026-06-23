from django.contrib import admin

# Register your models here.
from .models import Opportunity

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'date_scraped')
    search_fields = ('title', 'company')