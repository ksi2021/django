from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# User = get_user_model()


def validate_image(image):
    file_size = image.file.size
    limit_mb = 2
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError('Максимальный размер файла %s MB' % limit_mb)
    # file_size = image.file.size
    # limit_kb = 150
    # if file_size > limit_kb * 1024:
    #     raise ValidationError('Max size of file is %s KB' % limit)


class UserData(AbstractUser):
    phone = models.CharField(max_length=15, verbose_name='Номер телефона', null=True, blank=True, unique=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', null=True, blank=True,
                                    related_name='related_order')
    used_coupons = models.ManyToManyField('Coupon', null=True, blank=True, verbose_name='Использованные купоны',
                                          related_name='related_coupon')
    first_name = models.CharField(verbose_name='Имя', max_length=150)

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        return 'Покупатель: {}'.format(self.first_name)


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название категории')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Products(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', null=True,
                                 related_name='category')
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=128, blank=True, null=True)
    price = models.DecimalField(max_digits=4, decimal_places=0, default=375)
    price2 = models.DecimalField(max_digits=4, decimal_places=0, null=True, default=579)
    price3 = models.DecimalField(max_digits=4, decimal_places=0, null=True, default=699)
    image = models.ImageField(upload_to='img/product/',
                              validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg']),
                                          validate_image])
    slug = models.SlugField(unique=True)
    is_custom = models.BooleanField(null=True, blank=True, default=False)

    def __str__(self):
        return 'Продукт: {}, Категория: {}'.format(self.name, self.category)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['is_custom']


class CartProduct(models.Model):
    user = models.ForeignKey('UserData', verbose_name='Покупатель', on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    size = models.CharField(max_length=32, default=0)
    price = models.DecimalField(max_digits=4, decimal_places=0)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return 'Продукт: {} (для корзины)'.format(self.product.name)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Промежуточная(Продукут - Корзина)'
        verbose_name_plural = 'Промежуточные(Продукут - Корзина)'


class Cart(models.Model):
    owner = models.ForeignKey('UserData', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    # total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)
    date_create = models.DateTimeField(auto_now_add=True)
    qty = models.PositiveIntegerField(default=0)
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, null=True, blank=True)
    session = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELED = 'canceled'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен'),
        # (STATUS_CANCELED, 'Отменен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(UserData, verbose_name='Покупатель', related_name='related_orders',
                                 on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=128, verbose_name='Адрес', null=True, blank=True)
    entrance = models.CharField(max_length=128, verbose_name='Подъезд', null=True, blank=True)
    floor_number = models.CharField(max_length=128, verbose_name='Этаж', null=True, blank=True)
    apartment_number = models.CharField(max_length=128, verbose_name='Квартира', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказ',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания заказа')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения статуса')

    def __str__(self):
        return 'Заказ №{}'.format(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Coupon(models.Model):
    code = models.CharField(max_length=15, verbose_name='Купон', unique=True)
    sale = models.IntegerField(verbose_name='Скидка', validators=[MinValueValidator(1), MaxValueValidator(70)])

    # users = models.ManyToManyField(UserData, blank=True, null=True, related_name='related_coupon')

    def __str__(self):
        return '{}, {}%'.format(self.code, self.sale)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'


class Promotions(models.Model):
    title = models.CharField(max_length=128, verbose_name='Название акции')
    description = models.TextField()
    img = models.ImageField(upload_to='img/promotions/',
                            validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg']),
                                        validate_image])
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return 'Акция ({})'.format(self.product or self.coupon)

    def clean(self):
        if self.product and self.coupon:
            raise ValidationError('Либо продукт, либо промокод')

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
