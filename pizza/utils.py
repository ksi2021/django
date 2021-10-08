from django.db import models


def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if cart_data.get('final_price__sum'):
        try:
            cart.final_price = int(cart_data['final_price__sum']) * ((100 - cart.coupon.sale) / 100)
        except:
            cart.final_price = cart_data['final_price__sum']
    else:
        cart.final_price = 0
    cart_data = cart.products.all().aggregate(models.Sum('qty'), models.Count('id'))
    if cart_data.get('qty__sum'):
        cart.qty = cart_data['qty__sum']
    else:
        cart.qty = 0
    cart.total_products = cart_data['id__count']
    cart.save()
