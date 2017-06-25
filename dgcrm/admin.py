from django.contrib import admin
from django.db.models import ManyToManyField, ForeignKey

# from main.models import Result, ClientServiceLinker, ClientResultLinker
from .models import Feadback, Client, Event, Result, ClientServiceLinker#, ClientResultLinker



class FeadbackAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Feadback._meta.get_fields()]
    # fields = [field.name for field in Feadback._meta.get_fields()]
    list_display = [field.name for field in Feadback._meta.fields]
    fields = [field.name for field in Feadback._meta.fields if field.name not in ["id"]]
    readonly_fields = ("date",)

class ClientAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    # fields = [field.name for field in Client._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, ForeignKey)]
    list_display = [field.name for field in Client._meta.fields]
    fields = [field.name for field in Client._meta.fields if field.name not in ["id"]]
    readonly_fields = ("registration", )


class EventAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Event._meta.fields]
    fields = [field.name for field in Event._meta.fields if field.name not in ["id"]]
    # readonly_fields = ("date",)


class ResultAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Result._meta.fields]
    fields = [field.name for field in Result._meta.fields if field.name not in ["id"]]


class ClientServiceLinkerAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in ClientServiceLinker._meta.fields]
    fields = [field.name for field in ClientServiceLinker._meta.fields if field.name not in ["id"]]


# class ClientResultLinkerAdmin(admin.ModelAdmin):
    
#     list_display = [field.name for field in ClientResultLinker._meta.fields]
#     fields = [field.name for field in ClientResultLinker._meta.fields if field.name not in ["id"]]



admin.site.register(Feadback, FeadbackAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(ClientServiceLinker, ClientServiceLinkerAdmin)
# admin.site.register(ClientResultLinker, ClientResultLinkerAdmin)