from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('',views.index,name='index'),
    path('product/<int:id>',views.details,name='details'),
    path('checkout/<int:id>',views.create_checkout_session,name="checkout"),
    path('success/',views.payment_success_view,name='success'),
    path('failed/',views.payment_failed_view,name='failed'),
    
    path('create-product/',views.create_product,name='create_product'),
    path('edit-product/<int:id>',views.edit_product,name='edit_product'),
    path('delete-product/<int:id>',views.delete_product,name='delete_product'),
    
    path('dashboard',views.dashboard,name='dashboard'),
    path('user/register',views.register,name='register'),
    path('user/login',auth_views.LoginView.as_view(template_name='app/forms/login.html'),name="login"),
    path('logout',
        auth_views.LogoutView.as_view(template_name='app/forms/logout.html'),
        name="logout"
    ),
    path('invalid',views.invalid,name='invalid'),
    path('my-purchases',views.purchases,name='purchases'),
    path('sales-dashboard',views.sales_dashboard,name='sales_dashboard')
]

