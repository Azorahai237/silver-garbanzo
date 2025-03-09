from django.contrib import admin
from .models import Professor, Module, ModuleInstance, Rating
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('module_instance', 'professor', 'user', 'rating', 'last_updated')
    search_fields = ('professor__name', 'module_instance__module__name', 'user__username')


admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(ModuleInstance)
admin.site.register(Rating, RatingAdmin)
