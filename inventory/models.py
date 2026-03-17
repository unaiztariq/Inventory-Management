from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import CheckConstraint, Q
# Create your models here.



class Product(models.Model):
    price=models.DecimalField(max_digits=10,decimal_places=1)
    name= models.CharField(max_length=100,unique=True)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    stock=models.BigIntegerField(default=0)
    

    class Meta:
         
        unique_together = [['user', 'name']]
        constraints =[
            CheckConstraint( condition=Q(price__gte=0),name='price_cant_negative'),
            # CheckConstraint( condition=Q(stock__gte=0),name='out_of_stock')
            ]

class Sale(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    quantity= models.IntegerField(default=1)
    user= models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    date=models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        from django.core.exceptions import ValidationError
        print("hiiiiiiiiii")
        try:
            if self.product:
                if self.quantity>self.product.stock:  
                    raise ValidationError(f"quantity cannot exceed from  {self.product.stock}")
        except Product.DoesNotExist:
            return
        
        
        
    def save(self, *args, **kwargs):
        
        try:
            if self.product:
                self.total_amount = self.quantity * self.product.price
        except Product.DoesNotExist:
            return
        super().save(*args, **kwargs)
        


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    date = models.DateField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    quantity = models.BigIntegerField()
    total_expense =models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        
        try:
            if self.product:
                self.total_expense = self.quantity * self.product.price
        except Product.DoesNotExist:
            return
        super().save(*args, **kwargs)

