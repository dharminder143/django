from django import template
from blog.models import *
from django.template import Context
register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].orderitems.count()
    return 0


@register.filter
def cash_total(user):
	if user.is_authenticated:
		total=Order.objects.filter(user=user,ordered=False)
		if total:
			t=total[0].get_totals()
			return t
		else:
			return 0
	else:
		return 0

@register.simple_tag
def subcategory_list():
	total=subcategory.objects.all()
	return total

@register.filter
def wish_count(user):
	 if user.is_authenticated:
	 	qs = Wish.objects.filter(user=user).count()
	 	return qs
	 return 0

# @register.filter
# def order_count_list(user):
# 	 if user.is_authenticated:
# 	 	qs = Order.objects.filter(user=user,ordered=False)
# 	 	return qs
# 	 return 0

@register.simple_tag
def order_count_list():
	qs = Order.objects.filter(ordered=False)
	ad = qs[0].orderitems.filter(purchased=False)
	if qs.exists():
		return ad
	else:
		return 0
	return 0 

@register.simple_tag
def cart_count_list():
	qs = Order.objects.filter(ordered=False)
	return qs