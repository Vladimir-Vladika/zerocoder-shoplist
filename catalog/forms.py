from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Электронная почта", required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "description", "image", "price", "shop_addresses")
        widgets = {"shop_addresses": forms.Textarea(attrs={"rows": 4, "placeholder": "Один адрес в каждой строке"}), "description": forms.Textarea(attrs={"rows": 4})}

    def clean_shop_addresses(self):
        value = self.cleaned_data["shop_addresses"]
        addresses = [line.strip() for line in value.splitlines() if line.strip()]
        if not addresses:
            raise forms.ValidationError("Укажите хотя бы один адрес.")
        return "\n".join(addresses)
