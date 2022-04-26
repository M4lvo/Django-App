from django.contrib import admin
from .models import Product
from .models import Purchase
from .models import Sale

admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Sale)



