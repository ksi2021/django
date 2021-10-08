import json
import random
from django.urls import reverse_lazy, reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from faker import Faker
from .forms import *
from .models import *
from .utils import recalc_cart

fake = Faker('ru_RU')


class UserTest(TestCase):

    def setUp(self) -> None:
        self.user = UserData.objects.create_user(username='eugene', password='5338', first_name=fake.first_name())
        self.user.set_password(self.user.password)

    def test_correct(self):
        user = self.client.login(username=self.user.username, password='5338')
        self.assertTrue(user)

    def test_wrong_username(self):
        user = self.client.login(username='wrong', password='5338')
        self.assertFalse(user)

    def test_wrong_pssword(self):
        user = self.client.login(username='eugene', password='wrong')
        self.assertFalse(user)

    def test_logout(self):
        user = self.client.login(username='eugene', password='5338')
        session_id = self.client.session['_auth_user_id']
        self.client.logout()
        self.assertNotIn(session_id, self.client.session)

    def test_form(self):
        form_data = {'username': 'qweqwe', 'first_name': 'вфвфы', 'phone': '123',
                     'password1': 'https://developer.mozilla.org/ru/docs/Learn/Server-side/Django/Testing',
                     'password2': 'https://developer.mozilla.org/ru/docs/Learn/Server-side/Django/Testing'}
        form = RegForm(form_data)

    def tearDown(self):
        self.user.delete()


class ProductToCartTest(TestCase):
    def summ(self):
        summa = 0
        for i in self.cart.products.all():
            summa += i.final_price
        return summa

    def setUp(self) -> None:
        self.user = UserData.objects.create_user(username='eugene', password='5338')
        self.category = Category.objects.create(name='test')
        self.product = Products.objects.create(
            category=self.category,
            name='test',
            description='test',
            image='test.png',
            slug='test-slug'
        )
        self.cart = Cart.objects.create(owner=self.user)
        self.cart_product = CartProduct.objects.create(
            user=self.user,
            cart=self.cart,
            price=self.product.price,
            product=self.product,
            qty=2
        )
        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)

    def test_category_in_product(self):
        self.assertEqual(self.category, self.product.category)

    def test_cart_product(self):
        url = '/add/{}/?size=25'.format(self.product.slug)
        self.client.post(url, {'price': 325})
        self.assertEqual(self.cart.final_price, self.summ())
        self.assertIn(self.cart_product, self.cart.products.all())

    def test_change_qty_cart_product(self):
        randomQTY = random.randint(1, 5)
        self.cart_product.qty = randomQTY
        recalc_cart(self.cart)
        self.assertEqual(self.cart_product.qty, randomQTY)
        self.assertEqual(self.cart.final_price, self.summ())
        self.assertIn(self.cart_product, self.cart.products.all())

    def test_delete_cart_product(self):
        self.cart.products.remove(self.cart_product)
        recalc_cart(self.cart)
        self.assertNotIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.final_price, self.summ())

    def test_custom(self):
        response = self.client.post(reverse('custom'),
                                    {'slug': 'test', 'description': 'test', 'price': 569, 'size': '25'})
        self.assertEqual(response.status_code, 302)

    def test_order(self):
        if bool(random.getrandbits(1)):
            order = Order.objects.create(buying_type='delivery', cart=self.cart, customer=self.user,
                                         phone=fake.phone_number(),
                                         address=fake.address(), entrance=1, floor_number=1,
                                         apartment_number=1, comment=fake.text())
        else:
            order = Order.objects.create(buying_type='self', cart=self.cart, customer=self.user,
                                         phone=fake.phone_number(),
                                         comment=fake.text())
        order.status = 'in_progress'
        order.cart.in_order = True
        self.user.orders.add(order)
        self.assertIn(order, self.user.orders.all())
        # TODO сделать через клиент

    def test_coupon(self):
        coupon = Coupon.objects.create(code='test', sale=40)
        self.cart.coupon = coupon
        self.assertEqual(coupon, self.cart.coupon)
        self.user.used_coupons.add(coupon)
        self.assertIn(coupon, self.user.used_coupons.all())
