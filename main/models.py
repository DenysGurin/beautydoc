from django.db import models


# def directory_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return 'main/{0}/{1}/{2}'.format(instance.result.service.id, instance.client.id, filename)

def portfolio_path(instance, filename):
    return 'main/portfolio/%s'%(filename)


class Portfolio(models.Model):
    photo = models.FileField(upload_to=portfolio_path)
    name = models.CharField(max_length=60, blank = True)
    description = models.TextField(blank = True)

    def __str__(self):
        return "%s "%str(self.id)


class Review(models.Model):
    name = models.CharField(max_length=60)
    review = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank = True)
    
    def __str__(self):
        return "%s "%str(self.id)


class ServiceCategory(models.Model):
    name = models.CharField(max_length=60, default="", blank = True)
    description = models.TextField(default="", blank = True)

    def __str__(self):
        return "%s "%(self.name)


class Service(models.Model):
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=30, default="", blank = True)
    price = models.CharField(max_length=30, default="", blank = True)
    description = models.TextField(default="", blank = True)

    def __str__(self):
        return "%s "%(self.name)


class DetailedService(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=30, default="", blank = True)
    price = models.CharField(max_length=30, default="", blank = True)
    description = models.TextField(default="", blank = True)

    def __str__(self):
        return "%s - %s "%(self.name, self.description)


# class Result(models.Model):
#     service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
#     notes = models.TextField(default="", blank = True)
#     date = models.DateTimeField()
    
#     def __str__(self):
#         return "%s -> %s "%(self.service.name, self.date)

        
# class Client(models.Model):
#     first = models.CharField(max_length=30, default="", blank = True)
#     last = models.CharField(max_length=30, default="", blank = True)
#     tel = models.CharField(max_length=30, default="", blank = True)
#     email = models.EmailField(default="", blank = True)
#     services = models.ManyToManyField(DetailedService, through='ClientServiceLinker', related_name = 'client_service', blank=True)
#     results = models.ManyToManyField(Result, through='ClientResultLinker', related_name = 'client_result', blank=True)
#     registration = models.DateTimeField(auto_now_add=True, blank = True)
#     last_visit = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return "%s %s"%(self.first, self.last)


# class Feadback(models.Model):
#     first = models.CharField(max_length=30)
#     last = models.CharField(max_length=30)
#     tel = models.CharField(max_length=30)
#     wish = models.CharField(max_length=30)
#     email = models.EmailField(default="", blank = True)
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
#     date = models.DateTimeField(auto_now_add=True, blank = True)

#     def __str__(self):
#         return "%s %s -> %s "%(self.first, self.last, self.wish)


# class ClientServiceLinker(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
#     service = models.ForeignKey(DetailedService, on_delete=models.CASCADE, blank=True, null=True)
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