from django.shortcuts import render , redirect , get_object_or_404
from . models import *
from .forms import *
from django.contrib.auth import authenticate, login 
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.forms import modelformset_factory
from django.contrib import messages
import stripe
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.paginator import Paginator
import datetime



stripe.api_key = settings.STRIPE_SECRET_KEY 

def profile_list(request):
    profile_data= Profile.objects.filter(user=request.user)
    Order_data= Order.objects.filter(user=request.user,ordered=True)
    return render(request ,'blog/user_profile.html', {'profile_data':profile_data,
                                                        'Order_data':Order_data
                                                        })

def product (request):
    pro_list= Product.objects.filter(published=1).order_by('-updated_at')
    fruits_list= Product.objects.filter(category__name='fruit').order_by('-updated_at')
    Vegetables_list= Product.objects.filter(category__name='Vegetables').order_by('-updated_at')
    date = datetime.date.today()
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(7)
    entr = Product.objects.filter(created_at__range=[start_week, end_week])
    return render(request ,'blog/index.html', {'pro_list':pro_list,
                                                'fruits_list':fruits_list,
                                                'Vegetables_list':Vegetables_list,
                                                'entr':entr
                                                })

def published_views(request,pk):
    post =Product.objects.get(pk=pk)
    if post.published== 0:
        post.published= 1
        post.save()
        messages.info(request,'product is published')
    elif post.published== 1:
        post.published= 0
        post.save()
        messages.info(request,'product is unpublished')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 



def product_detail(request, pk):
    post = get_object_or_404(Product, pk=pk)
    return render(request, 'blog/product.html', {'post': post})


def price_greater(request):
    if 'filter_type' in request.GET and request.GET ["filter_type"]== "low":
        product= Product.objects.filter().order_by('price')
    else:
        product= Product.objects.filter().order_by('-price')
    paginator = Paginator(product, 8)
    page = request.GET.get('page')
    product = paginator.get_page(page)
    return render (request,'blog/all_product.html',{'product':product})

def wish1_add_to_card(request,pk):
    item = get_object_or_404(Wish,pk=pk)
    wished_item,created = Cart.objects.get_or_create(item=item.item.pk,
                                                        user = request.user,
                                                        purchased=False
                                                        )
    item.delete()
    messages.info(request,'The item was added to your cart')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_item, created = Cart.objects.get_or_create(item=item,
                                                    user=request.user,
                                                    purchased=False
                                                    ) 
     # Order.objects.create(ua = a, data = {"id":}) 
    order_qs = Order.objects.filter(user=request.user, 
                                    ordered=False
                                    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.orderitems.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, f"{item.name} quantity has updated.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            order.orderitems.add(order_item)
            messages.success(request, f"{item.name} has added to your cart.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        order = Order.objects.create(
            user=request.user)
        order.orderitems.add(order_item)
        messages.info(request, f"{item.name} has added to your cart.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

@login_required
def add_to_wishlist(request,pk):
   item = get_object_or_404(Product,pk=pk)
   wished_item,created = Wish.objects.get_or_create(item=item,
                                                        user = request.user
                                                        )

   messages.info(request,'The item was added to your wishlist')
   return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def wish_list(request):
    wishh = Wish.objects.filter(user=request.user)
    return render(request,'blog/wish_list.html',{'wishh':wishh})

@login_required
def remove_wish(request,pk):
    item=get_object_or_404(Product,pk=pk)
    remove_list=Wish.objects.filter(item=item.pk,user=request.user)
    remove_list.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def Cart_view(request):
    user = request.user
    carts = Cart.objects.filter(user=user, purchased=False)
    orders = Order.objects.filter(user=user, ordered=False)
    if carts.exists():
        if orders.exists():
            order = orders[0]
            return render(request, 'blog/cart.html', {"carts": carts, 
                                                        'order': order
                                                        })
        else:
            messages.warning(request, "You do not have any item in your Cart")
            return redirect("product")
        
    else:
        messages.warning(request, "You do not have any item in your Cart")
        return redirect("product")

    return render(request,'blog/cart.html',{'carts':carts})

@login_required
def checkout(request):
    
    form = BillingForm
    
    order_qs = Order.objects.filter(user= request.user, ordered=False)
    order_items = order_qs[0].orderitems.all()
    order_total = order_qs[0].all_total() 
    get_total = order_qs[0].get_totals() 
    get_perse = order_qs[0].get_percentage() 

    context = {"form": form, 
                "order_items": order_items,
                "order_total": order_total,
                "get_total":get_total,
                "get_perse":get_perse
                 }

    # Getting the saved saved_address
    saved_address = BillingAddress.objects.filter(user = request.user)
    if saved_address.exists():
        savedAddress = saved_address.first()
        context = {"form": form, 
                    "order_items": order_items,
                    "order_total": order_total, 
                    "savedAddress": savedAddress
                    }

    if request.method == "POST":
        saved_address = BillingAddress.objects.filter(user = request.user)
        if saved_address.exists():

            savedAddress = saved_address.first()
            form = BillingForm(request.POST, instance=savedAddress)
            if form.is_valid():
                billingaddress = form.save(commit=False)
                billingaddress.user = request.user
                billingaddress.save()
        else:
            form = BillingForm(request.POST)
            if form.is_valid():
                billingaddress = form.save(commit=False)
                billingaddress.user = request.user
                billingaddress.save()
                
    return render(request, 'blog/checkout.html', context)

def payment(request):
    key = settings.STRIPE_PUBLISHABLE_KEY
    order_qs = Order.objects.filter(user= request.user, ordered=False)
    order_total = order_qs[0].all_total() 
    totalCents = float(order_total * 100);
    total = round(totalCents, 2)
    if request.method == 'POST':
        charge = stripe.Charge.create(amount=total,
            currency='usd',
            description=order_qs,
            source=request.POST['stripeToken'])
        # print(charge)
        
    return render(request, 'blog/payment.html', {"key": key, "total": total})

def charge(request):
    order = Order.objects.get(user=request.user, ordered=False)
    orderitems = order.orderitems.all()
    order_total = order.all_total() 
    totalCents = int(float(order_total * 100));
    if request.method == 'POST':
        charge = stripe.Charge.create(
                          amount=totalCents,
                          currency='usd',
                          description='Software development services',
                          shipping={
                            'name': 'Jenny Rosen',
                            'address': {
                              'line1': '510 Townsend St',
                              'postal_code': '98140',
                              'city': 'San Francisco',
                              'state': 'CA',
                              'country': 'US',
                            }
                          },
                          source='tok_visa',
                        )
        # print(charge)
        if charge.status == "succeeded":
            orderId = get_random_string(length=16, allowed_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            # print(charge.id)
            order.ordered = True
            order.paymentId = charge.id
            order.orderId = f'#{request.user}{orderId}'
            order.save()
            cartItems = Cart.objects.filter(user=request.user,purchased = False)
            for item in cartItems:
                item.purchased = True
                item.save()
                # item.delete()
        return render(request, 'blog/change.html', {"items": orderitems, "order": order })

def decreaseCart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.orderitems.filter(item =item.pk).exists():
            order_item = Cart.objects.filter(item=item,user=request.user)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.warning(request, f"{item.name} has removed from your cart.")

            else:
                order.orderitems.remove(order_item)
                order_item.delete()
                messages.warning(request, f"{item.name} has removed from your cart.")
            messages.info(request, f"{item.name} quantity has updated.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

        else:
            messages.info(request, f"{item.name} quantity has updated.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

    else:
        messages.info(request, "You do not have an active order")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 


def delete_cart(request, pk):
     item = get_object_or_404(Product, pk=pk)
     order_qs = Order.objects.filter(user=request.user, ordered=False)
     if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.orderitems.filter(item =item.pk).exists():
            order_item = Cart.objects.filter(item=item,user=request.user)[0]
            order.orderitems.remove(order_item)
            order_item.delete()
            messages.warning(request, f"{item.name} has removed from your cart.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.info(request, f"{item.name}You item is not delate")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
     else:
         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def login(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            login(user)
            return redirect('product')
    else:
        form = loginForm()
    return render(request, 'registration/login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Profile.objects.create(user=user)
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request)
        return redirect('login')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')
@login_required
def post_new(request):
    ImageFormSet = modelformset_factory(nave_header, fields=('image',), extra=3)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        # formset = ImageFormSet(request.POST or None, request.FILES or None )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_at = timezone.now()
            post.save()
            return redirect('product_list')

            # for f in formset:
            #     p=nave_header(post=post, image=f.cleaned_data['image'])
            #     p.save()
    else:
        form = ProductForm()
        # formset = ImageFormSet(queryset=nave_header.objects.none())

    return render(request, 'blog/post_edit.html', {'form': form })

@login_required
def product_list(request):
    list_display=Product.objects.filter(Q(author=request.user)).order_by('-updated_at')

    return render(request,'blog/product_list.html',{'list_display':list_display})
@login_required
def product_edit(request, pk):
    post = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.updated_at = timezone.now()
            post.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=post)
    return render(request, 'blog/product_edit.html', {'form': form})
@login_required
def post_remove(request, pk):
    post = get_object_or_404(Product, pk=pk)
    post.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def search(request):
    query = request.GET['query']
    if len(query) > 50:
        allpost= Product.objects.none()
    else:
        allpost=Product.objects.filter(Q(name__icontains=query)|
                                        Q(category__name__icontains=query)|
                                        Q(price__icontains=query))
    if allpost.count() == 0:
        messages.error(request,'can not found')
    return render(request,'blog/search.html',{'allpost':allpost, 'query':query})
    
def contact(request):
    if request.method == "POST":
        form = ContactusForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.info(request, "massage send")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = ContactusForm()
    return render(request, 'blog/contact.html', {'form': form })

def order_view(request):
    order_list=Order.objects.filter(user=request.user,ordered=True)
    # manyto=order_list[0].orderitems.all()
    address=BillingAddress.objects.filter(user=request.user)
    return render (request,'blog/order_list.html',{'order_list':order_list,
                                                    # 'manyto':manyto,
                                                    'address':address,
                                                    })

def add_all_pro(request):
    pro_list_all= Product.objects.filter(published=1).order_by('-updated_at')
    paginator = Paginator(pro_list_all, 8)
    page = request.GET.get('page')
    pro_list_all = paginator.get_page(page)
    return render(request,'blog/all_product.html',{'pro_list_all':pro_list_all})

def order_cat(request,pk):
    category_list= get_object_or_404(subcategory,pk=pk)
    category_post=Product.objects.filter(category=category_list)
    paginator = Paginator(category_post, 8)
    page = request.GET.get('page')
    category_post = paginator.get_page(page)
    return render (request,'blog/all_product.html',{'category_list':category_list,
                                                    'category_post':category_post
                                                        })

def weekly(request):
    date = datetime.date.today()
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(7)
    entries = Product.objects.filter(created_at__range=[start_week, end_week])
    return render (request,'blog/index.html',{'entries':entries})