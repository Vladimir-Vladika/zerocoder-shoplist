from decimal import Decimal
from tempfile import TemporaryDirectory
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Product
from PIL import Image
from io import BytesIO

class ShopTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.tmp.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.user = User.objects.create_user('user', password='some-strong-pass-123')
        self.manager = User.objects.create_user('manager', password='some-strong-pass-123')
        self.manager.groups.add(Group.objects.get(name='Менеджеры'))
        self.product = Product.objects.create(name='Чайник', price=Decimal('100.00'), image='products/example.jpg', shop_addresses='Томск, Ленина 1\nТомск, Мира 2')

    def test_catalog_search_and_detail(self):
        self.assertContains(self.client.get('/?q=чай'), 'Чайник')
        self.assertNotContains(self.client.get('/?q=телефон'), 'Чайник')
        self.assertContains(self.client.get(self.product.get_absolute_url()), 'Томск, Мира 2')

    def test_registration_creates_ordinary_user(self):
        response = self.client.post(reverse('register'), {'username': 'newuser', 'email': 'a@example.com', 'password1': 'VeryStrongPass123!', 'password2': 'VeryStrongPass123!'})
        self.assertRedirects(response, reverse('product_list'))
        new = User.objects.get(username='newuser')
        self.assertFalse(new.is_staff)
        self.assertFalse(new.groups.exists())
        self.assertNotEqual(new.password, 'VeryStrongPass123!')

    def test_access_control_and_delete_requires_post(self):
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)
        self.client.force_login(self.user)
        for url in [reverse('dashboard'), reverse('product_create'), reverse('product_update', args=[self.product.pk]), reverse('product_delete', args=[self.product.pk])]:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('product_delete', args=[self.product.pk])).status_code, 200)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
        self.client.post(reverse('product_delete', args=[self.product.pk]))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_manager_create_and_edit(self):
        self.client.force_login(self.manager)
        data = BytesIO()
        Image.new('RGB', (2, 2), 'red').save(data, 'PNG')
        image = SimpleUploadedFile('item.png', data.getvalue(), content_type='image/png')
        result = self.client.post(reverse('product_create'), {'name': 'Кружка', 'description': '', 'price': '123.00', 'shop_addresses': 'Адрес 1\nАдрес 2', 'image': image})
        self.assertRedirects(result, reverse('dashboard'))
        item = Product.objects.get(name='Кружка')
        result = self.client.post(reverse('product_update', args=[item.pk]), {'name': 'Чашка', 'description': '', 'price': '234.00', 'shop_addresses': 'Адрес 3'})
        self.assertRedirects(result, reverse('dashboard'))
        item.refresh_from_db()
        self.assertEqual(item.name, 'Чашка')
        self.assertEqual(item.addresses, ['Адрес 3'])
