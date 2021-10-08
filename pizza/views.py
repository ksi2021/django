import json

import stripe
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, auth_login, PasswordChangeView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .forms import RegForm, UpdateUserData
from .mixins import CartMixin
from .models import UserData, Products, CartProduct, Cart, Order, Coupon, Category, Promotions
from .serializers import userSerializer, productSerializer, cartProductsSerializer, cartSerializer, orderSerializer, \
    categorySerializer, promotionsSerializer
from .utils import recalc_cart


# class IsWhoUser(BasePermission):
#
#     def has_permission(self, request, view):
#         return bool((request.user.is_superuser or request.user.is_staff) or (request.method in SAFE_METHODS))
#

# class user(ModelViewSet):
#     queryset = User.objects.order_by()
#     serializer_class = userReal
#     model = User

class userAPI(ModelViewSet):
    # permission_classes = [IsWhoUser]
    serializer_class = userSerializer

    def get_queryset(self):
        return UserData.objects.filter(id=self.request.user.id)


class categoryApi(ModelViewSet):
    # permission_classes = [IsWhoUser]
    queryset = Category.objects.all()
    serializer_class = categorySerializer


class productsAPI(ModelViewSet):
    # permission_classes = [IsWhoUser]
    queryset = Products.objects.filter(is_custom=False)
    serializer_class = productSerializer


class promotionsAPI(ModelViewSet):
    # permission_classes = [IsWhoUser]
    queryset = Promotions.objects.all()
    serializer_class = promotionsSerializer


class cartProductsAPI(ModelViewSet):
    # permission_classes = [IsWhoUser]
    serializer_class = cartProductsSerializer

    def get_queryset(self):
        return CartProduct.objects.filter(user=self.request.user.id)


class cartAPI(ModelViewSet):
    # permission_classes = [IsWhoUser]
    serializer_class = cartSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(owner=self.request.user.id, in_order=False)
        else:
            if not self.request.session.session_key:
                self.request.session.save()
            return Cart.objects.filter(session=self.request.session.session_key, in_order=False)


class orderAPI(ModelViewSet):
    # permission_classes = [IsWhoUser]
    serializer_class = orderSerializer
    queryset = Order.objects.order_by()


class index(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'main.html', {'promotions': Promotions.objects.all()})


class login(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        # if self.request.recaptcha_is_valid:
            Cart.objects.filter(session=self.request.session.session_key).delete()
            auth_login(self.request, form.get_user())
            return HttpResponseRedirect(self.get_redirect_url())
        # else:
        #     return HttpResponseRedirect(reverse('login'))

    def get_redirect_url(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return '/admin'
        else:
            return '/'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        return super().get(request, *args, **kwargs)


class register(generic.CreateView):
    template_name = 'register.html'
    model = UserData
    form_class = RegForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # if self.request.recaptcha_is_valid:
            Cart.objects.filter(session=self.request.session.session_key).delete()
            form.save()
            return HttpResponseRedirect(reverse('login'))
        # else:
        #     return HttpResponseRedirect(reverse('register'))

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        return super().get(request, *args, **kwargs)


# class Logout(LogoutView):
#     template_name = 'logout.html'


class Profile(generic.View):
    def get(self, request, *args, **kwargs):
        # user, created = UserData.objects.get_or_create(id=self.cart.owner_id)
        try:
            user = SocialAccount.objects.get(user=request.user)
        except:
            user = UserData.objects.get(id=request.user.id)
        return render(request, 'profile.html', {'user': user})


class DeleteUserView(LoginRequiredMixin, generic.DeleteView):
    model = UserData
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class ChangeUserInfoView(generic.UpdateView, LoginRequiredMixin):
    model = UserData
    template_name = 'changeUserData.html'
    form_class = UpdateUserData
    success_url = reverse_lazy('user_profile')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class ChangePasswdView(PasswordChangeView, LoginRequiredMixin):
    template_name = 'changePassWD.html'
    success_url = reverse_lazy('user_profile')

    # def post(self, request, *args, **kwargs):
    #     print(123)


class AddToCartView(CartMixin, generic.View):
    def post(self, request, *args, **kwargs):
        # for text
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
        except:
            body = request.POST
        # end
        product = Products.objects.get(slug=kwargs.get('slug'))
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart,
            size=request.GET['size'], price=body['price'], product=product
        )
        if created:
            self.cart.products.add(cart_product)
        else:
            cart_product.qty += 1
            cart_product.save()
        recalc_cart(self.cart)
        return HttpResponseRedirect(reverse('index'))


class DeleteFromCartView(CartMixin, generic.View):

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # content_type = ContentType.objects.get(model=ct_model)
        product = Products.objects.get(slug=kwargs.get('slug'))
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product,
            size=body['size']
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        return HttpResponseRedirect('/basket/')


class ChangeQTYView(CartMixin, generic.View):

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # content_type = ContentType.objects.get(model=ct_model)
        product = Products.objects.get(slug=kwargs.get('slug'))
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product,
            size=body['size']
        )
        cart_product.qty = body['qty']
        cart_product.save()
        recalc_cart(self.cart)
        return HttpResponseRedirect(reverse('basket'))


class deleteCart(CartMixin):
    # Cart.objects.filter(owner=request.user.id).delete()
    def get(self, request, *args, **kwargs):
        self.cart.delete()
        return HttpResponseRedirect(reverse('basket'))


class basket(CartMixin, generic.View):

    def get(self, request, *args, **kwargs):
        if Order.objects.filter(cart=self.cart, cart__in_order=False, status='new').first():
            return HttpResponseRedirect(reverse('order'))
        context = {
            'cart': self.cart,
        }
        return render(request, 'basket.html', context)

    def post(self, request, *args, **kwargs):
        coupon = Coupon.objects.all()
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if not request.user.is_authenticated:
            return JsonResponse({'data': 'Чтобы использовать промокод надо авторизоваться.'})
        if self.cart.coupon or self.cart.owner.used_coupons.all().filter(
                related_coupon__used_coupons__code=body['code']):
            return JsonResponse({'data': 'Этот промокод уже был использован.'})
        else:
            if coupon.filter(code=body['code']):
                self.cart.coupon = coupon.filter(code=body['code']).first()
                self.cart.save()
                recalc_cart(self.cart)
            # for i, obj in enumerate(coupon):
            #     if obj.code == body['code']:
            #         self.cart.coupon = obj
            #         self.cart.save()
            #         recalc_cart(self.cart)
            return JsonResponse({'data': 'Такого промокода нет.'})

    def delete(self, request, *args, **kwargs):
        self.cart.coupon = None
        self.cart.save()
        recalc_cart(self.cart)
        return HttpResponseRedirect(reverse('index'))
        # if self.cart.is_coupon_activate:
        #     return JsonResponse({'data': 'Вы уже использовали промокод.', 'status': 1})
        # for i, obj in enumerate(coupon):
        #     if obj.code == body['code']:
        #         if len(obj.users.all()) == 0:
        #             self.cart.final_price = int(self.cart.final_price) * (100 - obj.sale) / 100
        #             self.cart.is_coupon_activate = True
        #             obj.users.add(self.cart.owner)
        #             self.cart.save()
        #             return JsonResponse({'data': 'Промокод активирован.', 'status': 2})
        #         # for j in obj.users.all():
        #         #     if j == self.cart.owner:
        #         #         return JsonResponse({'data': 'Вы уже использовали этот промокод'})
        #         for j in obj.users.all():
        #             if j != self.cart.owner:
        #                 self.cart.final_price = int(self.cart.final_price) * (100 - obj.sale) / 100
        #                 self.cart.is_coupon_activate = True
        #                 obj.users.add(self.cart.owner)
        #                 self.cart.save()
        #                 return JsonResponse({'data': 'Промокод активирован.', 'status': 3})
        #         print(list(obj.users.all()).index(request.user))
        #         self.cart.final_price = int(self.cart.final_price) * (100 - obj.sale) / 100
        #         self.cart.save()
        # for j in obj.users.all():
        #     print(j.id, self.cart.owner_id)
        #     if obj.code == request.POST['code'] and j.id != self.cart.owner_id:
        #         obj.users.add(self.cart.owner)
        #         self.cart.final_price = int(self.cart.final_price) * (100 - obj.sale) / 100
        #         self.cart.save()
        #         obj.save()
        #         return HttpResponseRedirect(reverse('basket'))


class order(CartMixin, generic.View):
    def get(self, request, *args, **kwargs):
        stripe.api_key = 'sk_test_51IgOVCHac5lTiSCzjs3ZKXz3C9o6WtQ0w03byY1RGR0fbrVbt0vOAcePoe7AfXPKYlIE9OJAsr2thd6cf3s8hBkE00LLZ5Sn4N'
        intent = stripe.PaymentIntent.create(
            amount=int(self.cart.final_price * 100),
            currency='rub',
            metadata={'integration_check': 'accept_a_payment'}
        )
        try:
            order = Order.objects.get(customer=self.cart.owner, cart=self.cart)
        except:
            order = None
        context = {
            'order': order,
            'cart': self.cart,
            'client_secret': intent.client_secret
        }
        return render(request, 'order.html', context)

    def post(self, request, *args, **kwargs):
        # requests.post('ws://localhost:8000/order/', json={'qwe': 123})
        req = request.POST
        try:
            order, created = Order.objects.get_or_create(
                customer=self.cart.owner,
                phone=req['tel'], cart=self.cart, buying_type=req['buying_type'],
                address=req['address'], entrance=req['entrance'],
                floor_number=req['floor_number'],
                apartment_number=req['apartment_number'], comment=req['comment'] or None
            )
        except MultiValueDictKeyError:
            order, created = Order.objects.get_or_create(
                customer=self.cart.owner,
                phone=req['tel'], cart=self.cart, buying_type=req['buying_type'], comment=req['comment'] or None
            )

        if created and self.cart.owner is not None:
            self.cart.owner.orders.add(order)
            self.cart.owner.phone = req['tel']
            self.cart.owner.save()
        return HttpResponseRedirect(reverse('order'))

    def delete(self, request, *args, **kwargs):
        Order.objects.filter(customer_id=self.cart.owner_id, cart__in_order=False).first().delete()
        return HttpResponseRedirect(reverse('basket'))


class OrderPayment(CartMixin, generic.View):
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(customer=self.cart.owner_id, cart=self.cart)
        order.status = 'in_progress'
        order.save()
        # for i in self.cart.products.all().filter(product__is_custom=True):
        #     i.product.delete()
        self.cart.in_order = True
        self.cart.save()
        if self.cart.owner and self.cart.coupon and not (self.cart.owner.is_superuser or self.cart.owner.is_staff):
            self.cart.owner.used_coupons.add(self.cart.coupon)
        return HttpResponseRedirect(reverse('index'))

    def get(self, request, *args, **kwargs):
        if not self.cart.products.all():
            return HttpResponseRedirect(reverse('index'))


class PromotionsView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'promotions.html')


class Custom(CartMixin):
    def get(self, request, *args, **kwargs):
        return render(request, 'custom.html')

    def post(self, request, *args, **kwargs):
        # for test
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
        except:
            body = request.POST
        # end test
        product, created = Products.objects.get_or_create(name='Моя пицца', description=body['description'],
                                                          price=body['price'],
                                                          image='img/product/custom.png', slug=body['slug'],
                                                          is_custom=True)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart,
            size=body['size'], price=body['price'], product=product
        )
        if created:
            self.cart.products.add(cart_product)
        else:
            cart_product.qty += 1
            cart_product.save()
        recalc_cart(self.cart)
        return HttpResponseRedirect(reverse('custom'))


class Staff(generic.View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return render(request, 'staffOrder.html')
        else:
            return HttpResponseRedirect(reverse('index'))

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        order = Order.objects.filter(id=body['id']).first()
        order.status = body['status']
        order.save()
        return HttpResponseRedirect(reverse('staff'))
