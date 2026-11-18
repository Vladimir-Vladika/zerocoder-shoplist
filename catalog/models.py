from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from decimal import Decimal

class Product(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="products/")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    shop_addresses = models.TextField("Адреса магазинов", help_text="Каждый адрес с новой строки")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.pk])

    @property
    def addresses(self):
        return [address.strip() for address in self.shop_addresses.splitlines() if address.strip()]
