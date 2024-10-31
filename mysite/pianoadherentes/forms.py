from django.forms import ModelForm
from django import forms
from .models import Titular, Adherente, Prestamos, Contratos


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
                    'is_active',
                    'plan'
                    ]

class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Fecha de inicio')
    end_date = forms.DateField(label='Fecha de fin')



class ClientFormPrestamos(ModelForm):
    cbu = forms.CharField(required=False)
    class Meta:
        model = Prestamos
        fields = ['name', 
                  'last_name',
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
        
class ContratosForm(ModelForm):
    class Meta:
        model = Contratos
        fields = ['date_init',
                    'date_end',
                    'price'
                    ]
