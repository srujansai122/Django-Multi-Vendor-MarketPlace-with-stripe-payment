from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,OrderDetail
from django.http import JsonResponse,HttpResponseNotFound
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.urls import reverse
from .forms import ProductForm ,UserRegistrationForm
from django.db.models import Sum
import datetime

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
    product=Product.objects.get(id=order.product.id)
    product.total_sales_amount+=int(order.amount)
    product.total_sales+=1
    product.save()
    order.save()
    return render(request,'app/payment_success.html',{'order':order,'download_image_quantity': range(order.quantity)})    


def payment_failed_view(request):
    return render(request,'app/payment_failed.html')


def create_product(request):
    if request.method=='POST':
        productForm=ProductForm(request.POST,request.FILES)
        if productForm.is_valid():
            new_prodouct=productForm.save(commit=False)
            new_prodouct.seller=request.user
            new_prodouct.save()
            return redirect('index')    
    productForm=ProductForm()
    context={
        'product_form':productForm
    }
    return render(request,'app/forms/create_product.html',context)


def edit_product(request,id):
    product=Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect('invalid')
        
    if request.method=='POST':
        productForm=ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            new_prodouct=productForm.save()
            return redirect('index')    
    productForm=ProductForm(instance=product)
    context={
        'product_form':productForm,
        'product':product
    }
    return render(request,'app/forms/edit_product.html',context)


def delete_product(request,id):
    product=Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect('invalid')
    if request.method=='POST':
        product.delete()
        return redirect('index')
    return render(request,'app/forms/delete_product.html',{'product':product})
    
    
def dashboard(request):
    products=Product.objects.filter(seller=request.user)
    return render(request,'app/dashboard.html',{'products':products})


def register(request):
    registration_form=UserRegistrationForm(request.POST or None)
    if request.method=='POST':
        if registration_form.is_valid():
            registration_form.save()
            return redirect('login')
    return render(request,'app/forms/register.html',{'registration_form':registration_form})

def invalid(request):
    return render(request,'app/invalid.html')


def purchases(request):
    orders=OrderDetail.objects.filter(customer_email=request.user.email)
    return render(request,'app/purchases.html',{'my_orders':orders})


def sales_dashboard(request):
    orders=OrderDetail.objects.filter(product__seller=request.user)
    total_sales=orders.aggregate(Sum('amount'))

    last_year=datetime.date.today()-datetime.timedelta(days=365)
    data=OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_year)
    yearly_sales=data.aggregate(Sum('amount'))
    
    last_month=datetime.date.today()-datetime.timedelta(days=30)
    data=OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_month)
    monthly_sales=data.aggregate(Sum('amount'))
    
    last_week=datetime.date.today()-datetime.timedelta(days=7)
    data=OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_week)
    weekly_sales=data.aggregate(Sum('amount'))
    

    yesterday_date = datetime.date.today() - datetime.timedelta(days=1)
    yesterday_sales = OrderDetail.objects.filter(
        product__seller=request.user,
        created_on__date=yesterday_date
    ).aggregate(Sum('amount'))

    today_date = datetime.date.today()
    today_sales = OrderDetail.objects.filter(
        product__seller=request.user,
        created_on__date=today_date
    ).aggregate(Sum('amount'))
    
    
    daily_sales_sum=OrderDetail.objects.filter(product__seller=request.user).values('created_on__date').order_by('created_on__date').annotate(sum=Sum('amount'))
    
    product_sales_sum = (
    OrderDetail.objects
    .filter(product__seller=request.user)
    .values('product__name')
    .order_by('product__name')
    .annotate(sum=Sum('amount'))
    )    
    context = {
        'total_sales': total_sales,
        'yearly_sales': yearly_sales,
        'monthly_sales': monthly_sales,
        'weekly_sales': weekly_sales,
        'yesterday_sales': yesterday_sales,
        'today_sales':today_sales,
        'daily_sales_sum':daily_sales_sum,
        'product_sales_sum':product_sales_sum
    }
    return render(request,'app/sales.html',context)


def orders(request):
    orders=OrderDetail.objects.filter(customer_email=request.user.email)
    return render(request,'app/orders.html',{'orders':orders})