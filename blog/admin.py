from django.contrib import admin
from . models import *
# Register your models here.
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.contrib.admin import AdminSite


class ProfileInline(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    # def get_queryset(self, request):
    #     qs = super(UserAdmin, self).get_queryset(request)
    #     qs =  qs.filter(is_superuser=False)
    #     return qs

    inlines = (ProfileInline, )
    list_display=('username','email','is_active','date_joined')
    
	# list_select_related = ('Profile', )
	# def get_location(self, instance):
	# 	return instance.Profile.location
	# get_location.short_description = 'Location'

admin.site.register(User,UserAdmin)

class ProductAdmin(admin.ModelAdmin):
    def image_post(self,obj):
        return format_html('<img src="/media/{}" width="200" height="150"/>'.format(obj.image))

    list_display=('author','name','category','price',
    	'available','stock','brand_name','image_post')

    list_filter = ['author','category','brand_name','price']

    search_fields = ['author__username','category__name','name','description','price']
    readonly_fields=['image_post']

admin.site.register(Product,ProductAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display=['user','item','quantity','created','purchased']

admin.site.register(Cart,CartAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display=('user','get_products','ordered','paymentId','orderId')
    # 'get_quantity',
    def get_products(self, obj):
        return "\n".join([p.item.name for p in obj.orderitems.all()])

    def price_grt(self, obj):
        return "\n".join(str(p.get_total()) for p in obj.orderitems.all())

    def user_name(self, instance):
        return instance.all_total()


admin.site.register(Order,OrderAdmin)


admin.site.register(Profile)
admin.site.register(BillingAddress)
admin.site.register(subcategory)
admin.site.register(nave_header)
admin.site.register(Wish)
admin.site.register(Contactus)
# admin.site.unregister(Group)

class EventAdminSite(AdminSite):
    site_header = "UMSRA Events Admin"
    site_title = "UMSRA Events Admin Portal"
    index_title = "Welcome to UMSRA Researcher Events Portal"

event_admin_site = EventAdminSite(name='event_admin')


event_admin_site.register(User)
event_admin_site.register(Profile)
event_admin_site.register(BillingAddress)
event_admin_site.register(subcategory)
event_admin_site.register(nave_header)
event_admin_site.register(Wish)




