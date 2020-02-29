from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from haystack.forms import FacetedSearchForm
class loginForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password', )


class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'first_name','last_name','email','password1', 'password2')

class ProductForm(forms.ModelForm):
    # image = forms.ImageField(label='Image')
    class Meta:
        model = Product
        fields = ('category','name','slug','description',
                   'price','available','stock',
                   'image','old_price','brand_name','published','delivery_charges')

class nave_header_Form(forms.ModelForm):
    class Meta:
        model = nave_header
        fields= ('image',)


class BillingForm(forms.ModelForm):

    class Meta:
        model = BillingAddress
        fields = ['address', 'zipcode', 'city', 'landmark']

class ContactusForm(forms.ModelForm):
    class Meta:
        model= Contactus
        fields=['name','email','Enquiry']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control',
                                            'placeholder':'username'}),
            'email': forms.EmailInput(attrs={'class':'form-control',
                                            'placeholder':'Email'}),
            'Enquiry': forms.Textarea(attrs={'class':'form-control','rows':'10',
                                            'placeholder':'Enquiry'}),
                                            }