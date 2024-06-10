from django.forms import ModelForm
from .models import Titular, Adherente
class ClientForm(ModelForm):
    class Meta:
        model = Titular
        fields = ['name','phone','address','address_detail','dni','cbu','is_active']


class AdherenteForm(ModelForm):
    class Meta:
        model = Adherente
        fields = ['name','phone','address','address_detail','dni','is_active']


