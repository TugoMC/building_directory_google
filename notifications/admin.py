# notifications/admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'is_read', 'truncated_message')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    list_per_page = 25
    
    def truncated_message(self, obj):
        """Retourne un message tronqué pour l'affichage dans la liste"""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    truncated_message.short_description = 'Message'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marquée(s) comme lue(s).')
    mark_as_read.short_description = "Marquer les notifications sélectionnées comme lues"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marquée(s) comme non lue(s).')
    mark_as_unread.short_description = "Marquer les notifications sélectionnées comme non lues"
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('user', 'title', 'message', 'link')
        }),
        ('Statut', {
            'fields': ('is_read', 'created_at')
        }),
    )