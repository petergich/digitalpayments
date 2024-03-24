from django.urls import path, include
from . import views
urlpatterns = [
    path("",views.home,name="home"),
    path('mpesa/callback/', query_stk_status,name="status"),
    path('accesstoken/', views.get_access_token, name='get_access_token'),
    path('query/', views.query_stk_status, name='query_stk_status'),
    path('sellerlogin',views.sellerlogin,name='sellerlogin'),
    path('sellerregister',views.sellerregister,name="sellerregister"),
    path('customerregister',views.customerregister,name="customerregister"),
    path('customerlogin',views.customerlogin,name="customerlogin"),
    path('customerhome',views.customerhome,name="customerhome"),
    path("sellerhome",views.sellerhome, name="sellerhome"),
    path("sell",views.sell, name="sell"),
    path("customerdebit",views.customerdebit,name="customerdebit"),
    path("superadminhome",views.superadminhome,name="superadminhome"),
    path("requestprocess",views.requestprocess,name="requestprocess"),
    path("superadminlogin",views.superadminlogin,name="superadminlogin"),
    path("paymentinfo",views.paymentinfo,name="paymentinfo"),
]
