from django import forms
from .models import Order, Service


class OrderForm(forms.ModelForm):
    """
    Форма создания и редактирования заказа.

    Args:
        forms.ModelForm: Базовая форма Django для модели.
    Returns:
        OrderForm: Экземпляр формы заказа.
    """

    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'h-4 w-4 rounded border-white/20 bg-dark-800 accent-[#FFD60A]'
        }),
        label='Дополнительные услуги'
    )

    class Meta:
        """
        Настройки формы заказа.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки формы.
        """

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

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Инициализирует форму и выставляет выбранные услуги заказа.

        Args:
            *args: Позиционные аргументы формы.
            **kwargs: Именованные аргументы формы.
        Returns:
            None: Метод настраивает текущий экземпляр формы.
        """
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['services'].initial = self.instance.services.all()

    def save(self, commit: bool = True) -> Order:
        """
        Сохраняет заказ и выбранные дополнительные услуги.

        Args:
            commit: Нужно ли сразу сохранить объект в базу.
        Returns:
            Order: Сохранённый или подготовленный экземпляр заказа.
        """
        order = super().save(commit=commit)

        if commit:
            order.services.set(self.cleaned_data['services'])

        return order
