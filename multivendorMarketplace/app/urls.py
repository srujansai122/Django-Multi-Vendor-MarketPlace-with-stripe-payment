from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('product/<int:id>',views.details,name='details'),
    path('checkout/<int:id>',views.create_checkout_session,name="checkout"),
    path('success/',views.payment_success_view,name='success'),
    path('failed/',views.payment_failed_view,name='failed'),
]