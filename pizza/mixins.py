from django.views.generic import View

from .models import Cart, UserData


class CartMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = UserData.objects.filter(id=request.user.id).first()
            if not customer:
                customer = UserData.objects.create(id=request.user.id)
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            if not request.session.session_key:
                request.session.save()
            cart = Cart.objects.filter(for_anonymous_user=True, in_order=False,
                                       session=request.session.session_key).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True, session=request.session.session_key)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)
