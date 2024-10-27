from django.contrib import admin
from django.utils.html import format_html
from .models import Professionnel


@admin.register(Professionnel)
class ProfessionnelAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'city', 'commune', 
                   'specialization', 'skill_level', 'daily_rate', 
                   'display_availability', 'show_profile_photo')
    
    list_filter = ('city', 'commune', 'specialization', 'skill_level')
    search_fields = ('full_name', 'email', 'phone')
    
    fieldsets = (
        ('Informations Personnelles', {
            'fields': (
                'full_name', 'profile_photo', 'email', 'phone',
                'city', 'commune'
            )
        }),
        ('Média', {
            'fields': ('presentation_video',),
        }),
        ('Informations Professionnelles', {
            'fields': (
                'specialization', 'skill_level', 'certifications',
                'years_of_experience', 'daily_rate', 'availability'
            )
        }),
    )

    def display_availability(self, obj):
        return ", ".join(obj.get_workdays_list())
    display_availability.short_description = "Jours disponibles"

    def show_profile_photo(self, obj):
        if obj.profile_photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_photo.url
            )
        return "Aucune photo"
    show_profile_photo.short_description = "Photo"

    # Personnalisation des messages d'aide
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "availability":
            field.help_text = "Entrez les jours de disponibilité séparés par des virgules (ex: Lundi,Mardi,Mercredi)"
        elif db_field.name == "certifications":
            field.help_text = "Listez vos certifications, une par ligne"
        return field