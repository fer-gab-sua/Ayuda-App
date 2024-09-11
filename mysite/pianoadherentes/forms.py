from django.forms import ModelForm
from django import forms
from .models import Titular, Adherente


class ClientForm(ModelForm):
    class Meta:
        model = Titular
        fields = ['name', 
                  'last_name',
                  'document_type',
                  'document',
                  'birthdate',
                  'sex',
                  'street_address',
                  'number',
                  'floor',
                  'between_street',
                  'province',
                  'city',
                  'postal_code',
                  'phone',
                  'cbu',
                  'is_active'
                  ]


class AdherenteForm(ModelForm):
    class Meta:
        model = Adherente
        fields = ['name',
                    'last_name',
                    'document_type',
                    'document',
                    'birthdate',
                    'sex',
                    'street_address',
                    'number',
                    'floor',
                    'between_street',
                    'province',
                    'city',
                    'postal_code',
                    'phone',
                    'is_active'
                    ]

class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Fecha de inicio')
    end_date = forms.DateField(label='Fecha de fin')
