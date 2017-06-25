from django import forms
from .models import Review
from dgcrm.models import Feadback

# class FeadbackForm(forms.Form):
#     first = forms.CharField(max_length=30, label="First")
#     last = forms.CharField(max_length=30, label="Last")
#     tel = forms.CharField(max_length=30, label="Tel")
#     wish = forms.CharField(widget=forms.Textarea, label="Wish")
#     email = forms.EmailField(required=False, label="Email")


class FeadbackForm(forms.ModelForm): 
    email = forms.EmailField(required=False, label="Email")
    
    def __init__(self, *args, **kwargs):
        super(FeadbackForm, self).__init__(*args, **kwargs)
        placeholder_dict = {"First": "Имя",
                            "Last": "Фамилия",
                            "Tel": "Мобильный",
                            "Wish": "Сообщение",
                            "Email": "Email",
                            }
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field_name == "wish":
                field.widget = forms.Textarea(attrs={'placeholder': placeholder_dict[field.label],
                                                      'class': 'w3-input'})
                field.label = ""
            else:
                field.widget = forms.TextInput(attrs={'placeholder': placeholder_dict[field.label],
                                                      'class': 'w3-input'})
                field.label = ""
                
    class Meta:
        model = Feadback
        exclude = ["date", "has_event", "client"]
        # fields = ['first', 'last', 'tel', 'wish', 'email']


class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        placeholder_dict = {"Name": "Имя",
                            "Review": "Отзыв",
                            }
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field_name == "review":
                field.widget = forms.Textarea(attrs={'style': "width:100%;",
                                                     'placeholder': placeholder_dict[field.label],
                                                     'class': 'w3-input'})#'style': "width:100%;height:300px;", 
            else:
                field.widget = forms.TextInput(attrs={'style': "width:100%;", 
                                                      'placeholder': placeholder_dict[field.label],
                                                      'class': 'w3-input'})
    class Meta:
        model = Review
        fields = '__all__'