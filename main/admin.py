# import redis

from django.contrib import admin
from django.core.cache import cache
from django.db.models import ManyToManyField, ForeignKey
from .models import Portfolio, Review, ServiceCategory, Service, DetailedService

    
# class FeadbackAdmin(admin.ModelAdmin):
#     # list_display = [field.name for field in Feadback._meta.get_fields()]
#     # fields = [field.name for field in Feadback._meta.get_fields()]
#     list_display = [field.name for field in Feadback._meta.fields]
#     fields = [field.name for field in Feadback._meta.fields if field.name not in ["id"]]
#     readonly_fields = ("date",)

# class ClientAdmin(admin.ModelAdmin):
#     # list_display = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
#     # fields = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
#     list_display = [field.name for field in Client._meta.fields]
#     fields = [field.name for field in Client._meta.fields if field.name not in ["id"]]
#     readonly_fields = ("registration", )

class PortfolioAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    # fields = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    list_display = [field.name for field in Portfolio._meta.fields]
    fields = [field.name for field in Portfolio._meta.fields if field.name not in ["id"]]

class ReviewAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    # fields = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    list_display = [field.name for field in Review._meta.fields]
    fields = [field.name for field in Review._meta.fields if field.name not in ["id"]]
    readonly_fields = ("date",)

class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceCategory._meta.fields]
    fields = [field.name for field in ServiceCategory._meta.fields if field.name not in ["id"]]

class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    fields = [field.name for field in Service._meta.fields if field.name not in ["id"]]

class DetailedServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DetailedService._meta.fields]
    fields = [field.name for field in DetailedService._meta.fields if field.name not in ["id"]]
        

# admin.site.register(Feadback, FeadbackAdmin)
# admin.site.register(Client, ClientAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(DetailedService, DetailedServiceAdmin)