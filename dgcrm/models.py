from django.db import models
from main.models import DetailedService


def directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'main/{0}/{1}/{2}'.format(instance.detailed_service.id, instance.client.id, filename)


class Client(models.Model):
    first = models.CharField(max_length=30, default="", blank = True)
    last = models.CharField(max_length=30, default="", blank = True)
    tel = models.CharField(max_length=30, default="", blank = True)
    email = models.EmailField(default="", blank = True)
    registration = models.DateTimeField(auto_now_add=True, blank = True)
    birthday = models.DateField(blank = True, null=True)
    position = models.CharField(max_length=100, default="", blank = True)
    live_in = models.CharField(max_length=100, default="", blank = True)
    # services = models.ManyToManyField(DetailedService, through='ClientServiceLinker', related_name = 'client_service', blank=True)##del
    # events = models.ManyToManyField(Event, through='ClientEventLinker', related_name = 'client_event', blank=True)
    
    # last_visit = models.DateTimeField(blank=True, null=True)
    # total_paid = models.IntegerField(default=0, blank = True, null=True)

    def __str__(self):
        return "%s %s %s"%(self.first, self.last, self.tel)


class Feadback(models.Model):
    first = models.CharField(max_length=30)
    last = models.CharField(max_length=30)
    tel = models.CharField(max_length=30)
    wish = models.CharField(max_length=300, blank = True)
    email = models.EmailField(default="", blank = True)
    # client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank = True)
    has_event = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "%s %s %s-> %s "%(self.first, self.last, self.tel, self.wish)


class Result(models.Model):
    detailed_service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    photo = models.FileField(upload_to=directory_path, blank = True)
    notes = models.TextField()
    date = models.DateTimeField()
    
    def __str__(self):
        return "%s %s -> %s "%(self.client, self.detailed_service.name, self.date)


class Pay(models.Model):
    detailed_service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)##del
    pay = models.IntegerField()
    profit = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField()

class Price(models.Model):
    CURRENCY_CHOICES = (
        ("UAH", 'UAH'),
        ("USD", 'USD'),
        ("EUR", 'EUR'),
    )

    brutto_price = models.IntegerField(blank=True, null=True)
    customer_price = models.IntegerField()
    discount = models.IntegerField(default=0, blank=True, null=True)
    currency = models.CharField(max_length=20,
                                choices=CURRENCY_CHOICES,
                                default="UAH",)
    date = models.DateField(auto_now_add=True, blank = True)

    # def __init__(self, *args, **kwargs):
    #     super(Price, self).__init__(*args, **kwargs)
    #     self.CURRENCY_CHOICES = CURRENCY_CHOICES
    # @classmethod
    # def getCurrencyLong(cls, short, choices):
    #     for item in choices:
    #         if item[0] == short:
    #             return item[1]

    def __str__(self):
        return "%s %s"%(self.customer_price, self.currency)


class Event(models.Model):
    STATUS_CHOICES = (
        ("in_progress", 'ожидается'),
        ("successful", 'сделано'),
        ("failed", 'отменился'),
        ("contact", 'связаться'),
    )

    feadback = models.ForeignKey(Feadback, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True) ##del
    detailed_service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
    # detailed_services = models.ManyToManyField(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
    price = models.ForeignKey(Price, on_delete=models.CASCADE, blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    # successful = models.BooleanField(default=False, blank=True)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default="in_progress",)
    results = models.ManyToManyField(Result, related_name = 'results', blank=True)
    pays = models.ManyToManyField(Pay, related_name = 'pays', blank=True)
    def __str__(self):
        return "%s %s -> %s "%(self.client, self.detailed_service, self.date_time)

class Note(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE) 
    note = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank = True)

class Task(models.Model):
    task = models.TextField()
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    done = models.BooleanField(default=False)

class CanceledEvent(models.Model):
    feadback = models.ForeignKey(Feadback, on_delete=models.CASCADE, blank=True, null=True)
    detailed_service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
    price = models.CharField(max_length=30, default="", blank = True)
    brutto_price = models.IntegerField(blank = True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    successful = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "%s %s -> %s "%(self.feadback.client, self.detailed_service, self.date_time)




# class ClientServiceLinker(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
#     service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
#     date = models.DateTimeField()

#     def __str__(self):
#         return "%s %s - %s "%(self.client.first, self.client.last, self.service.name)


# class ClientEventLinker(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
#     date = models.DateTimeField()

#     def __str__(self):
#         return "%s %s - %s "%(self.client.first, self.client.last, self.event)





# class ClientPayLinker(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
#     pay = models.ForeignKey(Pay, on_delete=models.CASCADE, blank=True, null=True)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
#     date = models.DateTimeField()

#     def __str__(self):
#         return "%s %s - %s "%(self.client.first, self.client.last, self.service.name)


# class ServicePayLinker(models.Model):
#     service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
#     pay = models.ForeignKey(Pay, on_delete=models.CASCADE, blank=True, null=True)
#     date = models.DateTimeField()

#     def __str__(self):
#         return "%s %s - %s "%(self.client.first, self.client.last, self.service.name)


# class EventPayLinker(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
#     pay = models.ForeignKey(Pay, on_delete=models.CASCADE, blank=True, null=True)
#     date = models.DateTimeField()

#     def __str__(self):
#         return "%s %s - %s "%(self.client.first, self.client.last, self.service.name)


# class ClientResultLinker(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
#     result = models.ForeignKey(Result, on_delete=models.CASCADE, blank=True, null=True)
#     photo = models.FileField(upload_to=directory_path)
#     date = models.DateTimeField()

#     def __str__(self):
#         return "%s %s - %s "%(self.client.first, self.client.last, self.result.service.name)