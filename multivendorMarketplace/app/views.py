from django.shortcuts import render,get_object_or_404
from .models import Product,OrderDetail
from django.http import JsonResponse,HttpResponseNotFound
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.urls import reverse


# Create your views here.
def index(request):
    products=Product.objects.all()
    return render(request,'app/index.html',{'products':products})

def details(request,id):
    product=Product.objects.get(id=id)
    stripe_publishable_key= settings.STRIPE_PUBLIC_KEY
    stripe_secret_key=settings.STRIPE_SECRET_KEY
    return render(request,'app/detail.html',{'product':product, 'pk':stripe_publishable_key,'sk':stripe_secret_key})


@csrf_exempt
def create_checkout_session(request,id):
    request_data=json.loads(request.body)
    product=Product.objects.get(id=id)
    stripe.api_key=settings.STRIPE_SECRET_KEY
    quantity = int(request_data.get("quantity", 1))
    checkout_session=stripe.checkout.Session.create(
        customer_email=request_data['email'],
        payment_method_types=['card','upi'],
        line_items=[
            {
                'price_data':{
                    'currency':'inr',
                    'product_data':{
                        'name':product.name,
                    },
                    'unit_amount':int(product.price*100)                    
                },
                'quantity':int(quantity)
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('success'))+ "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('failed'))

    )
    
    order=OrderDetail()
    order.customer_email=request_data['email']
    order.product=product
    order.stripe_session_id = checkout_session.id
    order.amount=int(product.price)*int(request_data.get('quantity'))
    order.quantity=int(request_data['quantity'])
    order.save()
    
    return JsonResponse({'sessionId': checkout_session.id})


def payment_success_view(request):
    session_id=request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    stripe.api_key=settings.STRIPE_SECRET_KEY
    session=stripe.checkout.Session.retrieve(session_id)
    order = OrderDetail.objects.get(stripe_session_id=session.id)
    order.has_paid=True
    order.save()
    return render(request,'app/payment_success.html',{'order':order,'download_image_quantity': range(order.quantity)})    


def payment_failed_view(request):
    return render(request,'app/payment_failed.html')