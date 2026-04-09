from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme_preference', 'email_notifications', 'created_at']
    list_filter = ['theme_preference', 'email_notifications', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'location', 'birth_date', 'avatar')
        }),
        ('Preferences', {
            'fields': ('theme_preference', 'email_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )