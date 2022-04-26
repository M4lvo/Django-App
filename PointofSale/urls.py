from django.urls import path
from . import views

app_name = 'PointofSale'

urlpatterns = [
    path('', views.menu, name='menu'),
    path('newtrans/', views.newtransaction, name='transaction'),
    path('newproduct/', views.newproduct, name='product'),
    path('purchase/', views.purchase, name='purchase'),
    path('sale/', views.sale, name='sale'),
    path('ireport/', views.ireport, name='ireport'),
    path('preport/', views.preport, name='preport'),
    path('greport/', views.greport, name='greport'),
    path('gereport/', views.export_pos_excel, name='export_POS_excel'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('addtrans/', views.addtrans, name='addtrans'),
]
