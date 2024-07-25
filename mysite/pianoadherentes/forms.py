from django.forms import ModelForm
from django import forms
from .models import Titular, Adherente


class ClientForm(ModelForm):
    class Meta:
        model = Titular
        fields = ['name', 
                  'last_name',
                  'phone',
                  'street_address',
                  'number',
                  'document',
                  'cbu',
                  'is_active'
                  ]


class AdherenteForm(ModelForm):
    class Meta:
        model = Adherente
        fields = ['name',
                  'phone',
                  'street_address',
                  'number',
                  'document',
                  'is_active'
                  ]

class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Fecha de inicio')
    end_date = forms.DateField(label='Fecha de fin')
