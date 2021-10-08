from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from pizza import views, decorators
from rest_framework.routers import SimpleRouter
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='API "У Альбертовича"')

router = SimpleRouter()

router.register('api/products', views.productsAPI)
router.register('api/promotions', views.promotionsAPI)
router.register('api/category', views.categoryApi, basename='category')
router.register('api/cart_products', views.cartProductsAPI, basename='cart_products')
router.register('api/user', views.userAPI, basename='user')
router.register('api/cart', views.cartAPI, basename='cart')
router.register('api/order', views.orderAPI, basename='order')
# router.register('api/u', views.user, basename='u')

urlpatterns = [
    path('api/', schema_view),
    path('admin/', admin.site.urls, name='admin'),
    path('accounts/', include('allauth.urls')),
    path('', views.index.as_view(), name='index'),
    path('promotions/', views.PromotionsView.as_view(), name='promotions'),
    path('basket/', views.basket.as_view(), name='basket'),
    path('login/', decorators.check_recaptcha(views.login.as_view()), name='login'),
    path('register/', decorators.check_recaptcha(views.register.as_view()), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.Profile.as_view(), name='user_profile'),
    path('profile/change-passwd/', views.ChangePasswdView.as_view(), name='change_passwd'),
    path('profile/change-userdata/', views.ChangeUserInfoView.as_view(), name='change_userdata'),
    path('profile/delete/', views.DeleteUserView.as_view(), name='delete_user'),
    path('add/<str:slug>/', views.AddToCartView.as_view(), name='add'),
    path('remove-from-cart/<str:slug>/', views.DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('change-qty/<str:slug>/', views.ChangeQTYView.as_view(), name='change_qty'),
    path('delete-cart/', views.deleteCart.as_view(), name='delete_cart'),
    path('basket/order/', views.order.as_view(), name='order'),
    # path('basket/accept/', views.OrderAccept.as_view(), name='accept'),
    path('payed-online-order/', views.OrderPayment.as_view(), name='payment'),
    path('custom/', views.Custom.as_view(), name='custom'),
    path('staff/', views.Staff.as_view(), name='staff')
]

if settings.DEBUG:
    #     # urlpatterns += [
    #     #     url(r'^media/(?P<path>.*)$', serve, {
    #     #         'document_root': settings.MEDIA_ROOT,
    #     #     }),
    #     # ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += router.urls
