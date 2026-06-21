from django.db import models
# Create your models here.
class Product(models.Model):
    name=models.CharField(max_length=100)
    description=models.CharField(max_length=100)
    price=models.FloatField()
    file=models.FileField(upload_to='uploads')
    
    def __str(self):
        return self.name
    
    
class OrderDetail(models.Model):
    customer_email=models.EmailField()
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    amount= models.IntegerField()
    quantity=models.IntegerField(default=1)
    stripe_session_id = models.CharField(max_length=255, null=False, blank=False)
    has_paid=models.BooleanField(default=False)
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now_add=True)
    
