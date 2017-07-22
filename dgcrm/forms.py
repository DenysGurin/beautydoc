from django import forms
from django.forms import inlineformset_factory
from .models import Event, Result, Feadback, Pay, Task, Price, Client
# from main.models import 
from django.contrib.admin import widgets



class TaskForm(forms.ModelForm): 
    
    class Meta:
        model = Task
        fields = '__all__'

class EventForm(forms.ModelForm): 

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # placeholder_dict = {"First": "Имя",
        #                     "Last": "Фамилия",
        #                     "Tel": "Мобильный",
        #                     "Wish": "Сообщение",
        #                     "Email": "Email",
        #                     }
        
        # date_time = self.fields.get("date_time")
        # date_time.widget =widgets.AdminSplitDateTime()

        # notes.label = "Заметки"

            # else:
            #     field.widget = forms.TextInput(attrs={'placeholder': placeholder_dict[field.label],
            #                                           'class': 'w3-input'})
            #     field.label = ""

    class Meta:
        model = Event
        exclude = ["client", "feadback", "successful", "status", "results", "pays", "price"]
        
    # def __init__(self, *args, **kwargs):
    #     super(EventForm, self).__init__(*args, **kwargs)
    #     self.fields['data_time'].widget = widgets.AdminSplitDateTime()
    #     # self.fields['data_time'].widget.attrs['class'] = "datetimepicker"

class DetailedEventForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(DetailedEventForm, self).__init__(*args, **kwargs)
        # STATUS_CHOICES = (
        #     ("in_progress", 'ожидается'),
        #     ("successful", 'сделано'),
        #     ("failed", 'отменился'),
        #     ("contact", 'связаться'),
        # )
        status = self.fields.get("status")
        status.widget = forms.Select(attrs={'class': 'w3-select w3-bar-item w3-round-xlarge w3-white w3-hover-red w3-border w3-border-white', 'onchange': "this.form.submit()"})
        
        status.label = "Статус"

    class Meta:
        model = Event
        fields = ["status"]

class FeadbackForm(forms.ModelForm): 
    
    class Meta:
        model = Feadback
        exclude = ["client", "date", "has_event"]

class PriceForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(PriceForm, self).__init__(*args, **kwargs)
        
        CURRENCY_CHOICES = (
            ("UAH", 'UAH'),
            ("USD", 'USD'),
            ("EUR", 'EUR'),
        )
        brutto_price = self.fields.get("brutto_price")
        brutto_price.widget = forms.NumberInput(attrs={'placeholder': "", 'class': 'w3-input'})
        brutto_price.label = "Закупочная стоимость"

        customer_price = self.fields.get("customer_price")
        customer_price.widget = forms.NumberInput(attrs={'placeholder': "", 'class': 'w3-input'})
        customer_price.label = "Полная стоимость"

        discount = self.fields.get("discount")
        discount.widget = forms.NumberInput(attrs={'placeholder': "", 'class': 'w3-input'})
        discount.label = "Скидка %"

        currency = self.fields.get("currency")
        currency.widget = forms.Select(attrs={'class': 'w3-select'})
        currency.choices = CURRENCY_CHOICES
        # currency.initial = "UAH"
        currency.label = "Валюта"

    class Meta:
        model = Price
        fields = '__all__'

class ResultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)
        # placeholder_dict = {"First": "Имя",
        #                     "Last": "Фамилия",
        #                     "Tel": "Мобильный",
        #                     "Wish": "Сообщение",
        #                     "Email": "Email",
        #                     }
        
        notes = self.fields.get("notes")
        notes.widget = forms.Textarea(attrs={'placeholder': "", 'class': 'w3-input'})
        notes.label = "Заметки"

        date = self.fields.get("date")
        date.widget = forms.DateTimeInput(attrs={'placeholder': "", 'class': 'w3-input'})
        date.label = "Дата"

        photo = self.fields.get("photo")
        photo.widget = forms.FileInput(attrs={'placeholder': ""})
        photo.label = "Фото"
            # else:
            #     field.widget = forms.TextInput(attrs={'placeholder': placeholder_dict[field.label],
            #                                           'class': 'w3-input'})
            #     field.label = ""

    # successful = forms.BooleanField()
    # photo = forms.FileField()
    class Meta:
        model = Result
        exclude = ["client", "detailed_service"]

class PayForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(PayForm, self).__init__(*args, **kwargs)

        pay = self.fields.get("pay")
        pay.widget = forms.NumberInput(attrs={'placeholder': "", 'class': 'w3-input'})
        pay.label = "Сумма оплаты"

        date_time = self.fields.get("date_time")
        date_time.widget = forms.DateTimeInput(attrs={'placeholder': "", 'class': 'w3-input'})
        date_time.label = "Дата оплаты"

    class Meta:
        model = Pay
        exclude = ["client", "detailed_service", "profit"]

class TransferEventForm(forms.ModelForm):
    new_date_time = forms.DateTimeField()

class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)

        first = self.fields.get("first")
        first.widget = forms.TextInput(attrs={'placeholder': "", 'class': 'w3-input'})
        first.label = "Имя"

        last = self.fields.get("last")
        last.widget = forms.TextInput(attrs={'placeholder': "", 'class': 'w3-input'})
        last.label = "Фамилия"

        tel = self.fields.get("tel")
        tel.widget = forms.TextInput(attrs={'placeholder': "", 'class': 'w3-input'})
        tel.label = "Телефон"

        email = self.fields.get("email")
        email.widget = forms.EmailInput(attrs={'placeholder': "", 'class': 'w3-input'})
        email.label = "Email"

        birthday = self.fields.get("birthday")
        birthday.widget = forms.DateTimeInput(attrs={'placeholder': "", 'class': 'w3-input'})
        birthday.label = "Дата рождения"

        position = self.fields.get("position")
        position.widget = forms.TextInput(attrs={'placeholder': "", 'class': 'w3-input'})
        position.label = "Работает"

        live_in = self.fields.get("live_in")
        live_in.widget = forms.TextInput(attrs={'placeholder': "", 'class': 'w3-input'})
        live_in.label = "Проживает"

    class Meta:
        model = Client
        exclude = ["registration"]

class SearchForm(forms.Form):
    
    search = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "поиск",
                                                           'style': "border:none; ",
                                                           'autofocus': "none"}))

class SearchFeadbackForm(forms.Form):
    
    search = forms.CharField(widget=forms.TextInput(attrs={'id': "search_feadback",
                                                           'placeholder': "поиск",
                                                           'style': "border:none; ",
                                                           'autofocus': "none"}))



# class ReviewForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(ReviewForm, self).__init__(*args, **kwargs)
#         placeholder_dict = {"Name": "Имя",
#                             "Review": "Отзыв",
#                             }
#         for field_name in self.fields:
#             field = self.fields.get(field_name)  
#             if field_name == "review":
#                 field.widget = forms.Textarea(attrs={'style': "width:100%;",
#                                                      'placeholder': placeholder_dict[field.label],
#                                                      'class': 'w3-input'})#'style': "width:100%;height:300px;", 
#             else:
#                 field.widget = forms.TextInput(attrs={'style': "width:100%;", 
#                                                       'placeholder': placeholder_dict[field.label],
#                                                       'class': 'w3-input'})
#     class Meta:
#         model = Review
#         fields = '__all__'