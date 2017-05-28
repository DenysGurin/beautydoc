# import redis

from django.contrib import admin
from django.core.cache import cache
from django.db.models import ManyToManyField, ForeignKey
from .models import Feadback, Client, Portfolio, Review

    
class FeadbackAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Feadback._meta.get_fields()]
    # fields = [field.name for field in Feadback._meta.get_fields()]
    list_display = [field.name for field in Feadback._meta.fields if field.name != "id"]
    fields = [field.name for field in Feadback._meta.fields]

class ClientAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    # fields = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    list_display = [field.name for field in Client._meta.fields if field.name != "id"]
    fields = [field.name for field in Client._meta.fields]

class PortfolioAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    # fields = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    list_display = [field.name for field in Portfolio._meta.fields]
    fields = [field.name for field in Portfolio._meta.fields if field.name in ['description', 'name', 'photo']]

class ReviewAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    # fields = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    list_display = [field.name for field in Review._meta.fields if field.name != "id"]
    fields = [field.name for field in Review._meta.fields]

admin.site.register(Feadback, FeadbackAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Review, ReviewAdmin)