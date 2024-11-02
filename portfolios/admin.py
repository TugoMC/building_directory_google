from django.contrib import admin
from .models import Portfolio, PortfolioImage

class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'professionnel', 'created_at')
    list_filter = ('professionnel', 'created_at')
    search_fields = ('title', 'description', 'professionnel__full_name')
    inlines = [PortfolioImageInline]
    date_hierarchy = 'created_at'