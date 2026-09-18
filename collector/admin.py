from django.contrib import admin

from .models import Profile, Space, Testimonial


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "slug", "created_at")
    search_fields = ("name", "slug", "owner__username")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "space", "rating", "status", "is_featured", "created_at")
    list_filter = ("status", "rating", "is_featured", "is_liked")
    search_fields = ("client_name", "email", "company_role", "message")


admin.site.register(Profile)
