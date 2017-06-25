from django import forms
from django.forms import inlineformset_factory
from .models import Event, Result, Feadback
# from main.models import 
from django.contrib.admin import widgets


class EventForm(forms.ModelForm): 
    
    class Meta:
        model = Event
        exclude = ["client", "feadback", "successful"]
        
    # def __init__(self, *args, **kwargs):
    #     super(EventForm, self).__init__(*args, **kwargs)
    #     self.fields['data_time'].widget = widgets.AdminSplitDateTime()
    #     # self.fields['data_time'].widget.attrs['class'] = "datetimepicker"


class FeadbackForm(forms.ModelForm): 
    
    class Meta:
        model = Feadback
        exclude = ["client", "date", "has_event"]


class ResultForm(forms.ModelForm):

    successful = forms.BooleanField()
    photo = forms.FileField()
    class Meta:
        model = Result
        exclude = ["service", "client", "event"]

class TransferEventForm(forms.ModelForm):
    new_date_time = forms.DateTimeField()

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