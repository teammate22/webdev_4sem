from django import forms
from .models import Order, Service


class OrderForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'h-4 w-4 rounded border-white/20 bg-dark-800 accent-[#FFD60A]'
        }),
        label='Дополнительные услуги'
    )

    class Meta:
        model = Order
        fields = [
            'client',
            'driver',
            'tariff',
            'status',
            'from_address',
            'to_address',
            'price',
            'services',
            'receipt'
        ]
        widgets = {
            'client': forms.Select(attrs={
                'class': 'input-dark form-control w-full rounded-xl px-4 py-3'
            }),
            'driver': forms.Select(attrs={
                'class': 'input-dark form-control w-full rounded-xl px-4 py-3'
            }),
            'tariff': forms.Select(attrs={
                'class': 'input-dark form-control w-full rounded-xl px-4 py-3'
            }),
            'status': forms.Select(attrs={
                'class': 'input-dark form-control w-full rounded-xl px-4 py-3'
            }),
            'from_address': forms.TextInput(attrs={
                'class': 'input-dark form-control w-full rounded-xl px-4 py-3'
            }),
            'to_address': forms.TextInput(attrs={
                'class': 'input-dark form-control w-full rounded-xl px-4 py-3'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'input-dark form-control w-full rounded-xl px-4 py-3'
            }),
            'receipt': forms.ClearableFileInput(attrs={
                'class': 'input-dark form-control file-control w-full rounded-xl px-4 py-3'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['services'].initial = self.instance.services.all()

    def save(self, commit=True):
        order = super().save(commit=commit)

        if commit:
            order.services.set(self.cleaned_data['services'])

        return order
