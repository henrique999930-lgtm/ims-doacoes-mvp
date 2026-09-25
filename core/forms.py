from django import forms
from django.forms import formset_factory

from .models import Family, Item, StockMovement


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = [
            "nome_responsavel",
            "telefone",
            "quantidade_membros",
            "ativo",
            "observacoes",
        ]
        widgets = {
            "nome_responsavel": forms.TextInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "quantidade_membros": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class StockMovementForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=Item.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Item",
    )
    tipo = forms.ChoiceField(
        choices=StockMovement.TIPOS,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Tipo",
    )
    quantidade = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "min": "0.01"}
        ),
        label="Quantidade",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = Item.objects.filter(ativo=True).order_by("nome")


class DeliveryLineForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=Item.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Item",
    )
    quantidade = forms.DecimalField(
        required=False,
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "min": "0.01"}
        ),
        label="Quantidade",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = Item.objects.filter(ativo=True).order_by("nome")

    def clean(self):
        cleaned = super().clean()
        item = cleaned.get("item")
        quantidade = cleaned.get("quantidade")
        if bool(item) != bool(quantidade):
            raise forms.ValidationError("Informe o item e a quantidade na mesma linha.")
        return cleaned


DeliveryLineFormSet = formset_factory(DeliveryLineForm, extra=4)
