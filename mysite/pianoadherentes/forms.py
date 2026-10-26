from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import Titular, Adherente, Movimiento


class ClientForm(ModelForm):
    class Meta:
        model = Titular
        fields = ['name', 
                  'last_name',
                  'document_type',
                  'document',
                  'plan',
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
                    'plan'
                    ]

class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Fecha de inicio')
    end_date = forms.DateField(label='Fecha de fin')


class MovimientosForm(forms.Form):
    init_date = forms.DateField(label='Desde', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='Hasta (inclusive)', widget=forms.DateInput(attrs={'type': 'date'}))
    usuario = forms.ModelChoiceField(label='Usuario', queryset=User.objects.none(), required=False, empty_label='Todos')
    sucursal = forms.ChoiceField(label='Sucursal al momento del movimiento', required=False)
    tipo_persona = forms.ChoiceField(label='Persona', required=False, choices=[
        ('', 'Todas'), ('Titular', 'Titular'), ('Adherente', 'Adherente'),
    ])
    movimiento = forms.ChoiceField(label='Operacion', required=False, choices=[
        ('', 'Todas'), *Movimiento._meta.get_field('movimiento').choices,
    ])
    listado = forms.ChoiceField(label='Listado', choices=[
        ('todos', 'Todos los movimientos'),
        ('plus', 'Ventas Plus (incluye reingresos)'),
        ('reingresos', 'Solo reingresos a Plus para revisar'),
    ])

    def __init__(self, *args, usuarios, sucursales, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuario'].queryset = usuarios
        self.fields['sucursal'].choices = [('', 'Todas'), *[(s, s or 'Sin sucursal') for s in sucursales if s]]
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('init_date')
        fin = cleaned.get('end_date')
        if inicio and fin and inicio > fin:
            self.add_error('end_date', 'La fecha final debe ser igual o posterior a la inicial.')
        return cleaned
