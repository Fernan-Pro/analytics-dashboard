from django.contrib import admin

from producthunt.models import ProductHuntLaunch


@admin.register(ProductHuntLaunch)
class ProductHuntLaunchAdmin(admin.ModelAdmin):
    list_display = ("product_name", "votes", "launch_date")
    list_filter = ("launch_date",)
    search_fields = ("product_name", "tagline")
    date_hierarchy = "launch_date"
    ordering = ("-launch_date", "-votes")