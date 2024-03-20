from django.contrib import admin
from .models import User, Profile
# Register your models here.

# admin.site.register(User)
admin.site.register(Profile)


class CustomUserAdmin(admin.ModelAdmin):  # Assuming a custom User model admin
    search_fields = ('username', 'email',)  # Add relevant fields for searching
    # ... other admin configurations


admin.site.register(User, CustomUserAdmin)
