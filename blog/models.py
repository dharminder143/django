from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.forms import ModelForm
from django.dispatch import receiver
from django.db.models.signals import post_save
from ckeditor_uploader.fields import RichTextUploadingField
# from jsonfield import JSONField
# from phonenumber_field.modelfields import PhoneNumberField
# from ckeditor.fields import RichTextField


class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, null=False )
    username = models.CharField(max_length=30, unique=False)
    is_active = models.BooleanField( default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    seller = models.BooleanField(default=False)


    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField( upload_to='images/',blank=True)
    location = models.CharField(max_length=30, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.user.username

# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     instance.profile.save()

# class address(models.Model):
#     contact_no = PhoneNumberField(null=False, blank=False)
#     address = models.CharField(max_length=30,null=False)
#     country = models.CharField(max_length=30,null=False)
#     zipcode = models.CharField(max_length=30,null=False)


# class Category(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,related_name='children', db_index=True)
#     slug = models.SlugField()

#     class Meta:
#         unique_together = (('parent', 'slug',))
#         verbose_name_plural = 'categories'

    
#     def __str__(self):                           
#         full_path = [self.name]                  
#         k = self.parent
#         while k is not None:
#             full_path.append(k.name)
#             k = k.parent
#         return ' -> '.join(full_path[::-1])

class subcategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField()

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(subcategory, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = RichTextUploadingField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()
    image = models.ImageField( upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    brand_name = models.CharField(max_length=25, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.BooleanField(default=1)
    delivery_charges = models.PositiveIntegerField(default=0,blank=True)

    class Meta:
        ordering = ('name', )
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('shop:product_detail', args=[self.id, self.slug])

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total(self):
        total = self.item.price * self.quantity 
        floattotal = float("{0:.2f}".format(total))
        return floattotal


class Order(models.Model):
    orderitems  = models.ManyToManyField(Cart)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    paymentId = models.CharField(max_length=200, blank=True , null=True)
    orderId = models.CharField(max_length=200, blank=True, null=True)
    

    
    def __str__(self):
        return f"{self.user.username} "


    def get_totals(self):
        total = 0
        for order_item in self.orderitems.all():
            total += order_item.get_total()
        return total

    def get_delivery(self):
        for p in self.orderitems.all():
            d= p.quantity * p.item.delivery_charges
            return d

    def get_percentage(self):
        p = self.get_totals()*0.09
        return p
   
    def all_total(self):
        if self.get_delivery() >= 500 :
            return self.get_percentage()+self.get_totals()
        else :
            return self.get_percentage()+self.get_totals()+self.get_delivery()

class Wish(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.item.name

class nave_header(models.Model):
    image = models.ImageField( upload_to='images/', blank=True )
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    
class BillingAddress(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=50)
    city = models.CharField(max_length=30)
    landmark = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.user.username} billing address'

    class Meta:
        verbose_name_plural = "Billing Addresses"

class Contactus(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField(unique=False, null=False )
    Enquiry=models.CharField(max_length=500)
    def __str__(self):
        return self.name

