from django.contrib import admin
from django.db.models import ManyToManyField, ForeignKey

# from main.models import Result, ClientServiceLinker, ClientResultLinker
from .models import Feadback, Client, Event, Result, Pay, Task, Price# ClientServiceLinker#, ClientResultLinker


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

class ResultInline(admin.TabularInline):
    model = Event.results.through

class PayInline(admin.TabularInline):
    model = Event.pays.through

class EventAdmin(admin.ModelAdmin):
    inlines = [
        ResultInline,
        PayInline,
    ]

    list_display = [field.name for field in Event._meta.fields]
    # fields = [field.name for field in Event._meta.fields if field.name not in ["id"]]
    # # readonly_fields = ("date",)

class PriceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Price._meta.fields]
    fields = [field.name for field in Price._meta.fields if field.name not in ["id"]]
    readonly_fields = ("date",)

class ResultAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Result._meta.fields]
    fields = [field.name for field in Result._meta.fields if field.name not in ["id"]]


class PayAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Pay._meta.fields]
    fields = [field.name for field in Pay._meta.fields if field.name not in ["id"]]


class TaskAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Task._meta.fields]
    fields = [field.name for field in Task._meta.fields if field.name not in ["id"]]


# class ClientServiceLinkerAdmin(admin.ModelAdmin):
    
#     list_display = [field.name for field in ClientServiceLinker._meta.fields]
#     fields = [field.name for field in ClientServiceLinker._meta.fields if field.name not in ["id"]]


# class ClientResultLinkerAdmin(admin.ModelAdmin):
    
#     list_display = [field.name for field in ClientResultLinker._meta.fields]
#     fields = [field.name for field in ClientResultLinker._meta.fields if field.name not in ["id"]]



admin.site.register(Feadback, FeadbackAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Pay, PayAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Price, PriceAdmin)
# admin.site.register(ClientServiceLinker, ClientServiceLinkerAdmin)
# admin.site.register(ClientResultLinker, ClientResultLinkerAdmin)