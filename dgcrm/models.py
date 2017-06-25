from django.db import models
from main.models import DetailedService


def directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'main/{0}/{1}/{2}'.format(instance.service.id, instance.client.id, filename)


class Client(models.Model):
    first = models.CharField(max_length=30, default="", blank = True)
    last = models.CharField(max_length=30, default="", blank = True)
    tel = models.CharField(max_length=30, default="", blank = True)
    email = models.EmailField(default="", blank = True)
    services = models.ManyToManyField(DetailedService, through='ClientServiceLinker', related_name = 'client_service', blank=True)
    # results = models.ManyToManyField(Result, through='ClientResultLinker', related_name = 'client_result', blank=True)
    registration = models.DateTimeField(auto_now_add=True, blank = True)
    last_visit = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "%s %s %s"%(self.first, self.last, self.tel)


class Feadback(models.Model):
    first = models.CharField(max_length=30)
    last = models.CharField(max_length=30)
    tel = models.CharField(max_length=30)
    wish = models.CharField(max_length=300, blank = True)
    email = models.EmailField(default="", blank = True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank = True)
    has_event = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "%s %s %s-> %s "%(self.first, self.last, self.tel, self.wish)


class Event(models.Model):
    feadback = models.ForeignKey(Feadback, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    detailed_service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
    price = models.CharField(max_length=30, default="", blank = True)
    data_time = models.DateTimeField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    successful = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "%s %s -> %s "%(self.feadback.client, self.detailed_service, self.data_time)


class Result(models.Model):
    service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    photo = models.FileField(upload_to=directory_path, blank = True)
    notes = models.TextField(default="", blank = True)
    date = models.DateTimeField()
    
    def __str__(self):
        return "%s -> %s "%(self.service.name, self.date)


class CanceledEvent(models.Model):
    feadback = models.ForeignKey(Feadback, on_delete=models.CASCADE, blank=True, null=True)
    detailed_service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
    price = models.CharField(max_length=30, default="", blank = True)
    data_time = models.DateTimeField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    successful = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "%s %s -> %s "%(self.feadback.client, self.detailed_service, self.data_time)


class ClientServiceLinker(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField()

    def __str__(self):
        return "%s %s - %s "%(self.client.first, self.client.last, self.service.name)


# class ClientResultLinker(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
#     result = models.ForeignKey(Result, on_delete=models.CASCADE, blank=True, null=True)
#     photo = models.FileField(upload_to=directory_path)
#     date = models.DateTimeField()

#     def __str__(self):
#         return "%s %s - %s "%(self.client.first, self.client.last, self.result.service.name)