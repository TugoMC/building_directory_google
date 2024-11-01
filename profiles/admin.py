from django.contrib import admin
from django.utils.html import format_html
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'last_name', 'first_name', 'profession', 'city', 'commune', 'profile_image_display']
    list_filter = ['profession', 'city', 'commune']
    search_fields = ['user__email', 'last_name', 'first_name']
    readonly_fields = ['user']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def profile_image_display(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_image.url)
        return "Pas d'image"
    profile_image_display.short_description = 'Photo de profil'

    fieldsets = (
        ('Informations utilisateur', {
            'fields': ('user', 'profile_image')
        }),
        ('Informations personnelles', {
            'fields': ('last_name', 'first_name', 'profession')
        }),
        ('Localisation', {
            'fields': ('city', 'commune')
        }),
    )