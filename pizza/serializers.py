from rest_framework.serializers import ModelSerializer

from .models import Products, CartProduct, Cart, UserData, Order, Coupon, Category, Promotions


class categorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class productSerializer(ModelSerializer):
    category = categorySerializer(read_only=True)

    class Meta:
        model = Products
        fields = '__all__'


class cartProductsSerializer(ModelSerializer):
    product = productSerializer(read_only=True)

    class Meta:
        model = CartProduct
        fields = (
            'id',
            'user',
            'size',
            'price',
            'product',
            'qty',
            'final_price',
        )


class couponSerializer(ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class cartSerializer(ModelSerializer):
    products = cartProductsSerializer(read_only=True, many=True)
    coupon = couponSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'


class orderSerializer(ModelSerializer):
    cart = cartSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class promotionsSerializer(ModelSerializer):
    product = productSerializer(read_only=True)
    coupon = couponSerializer(read_only=True)

    class Meta:
        model = Promotions
        fields = '__all__'


# class userReal(ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'


class userSerializer(ModelSerializer):
    # user = userReal(read_only=True)

    class Meta:
        model = UserData
        fields = '__all__'
