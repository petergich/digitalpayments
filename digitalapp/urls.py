from django.urls import path, include
from . import views
urlpatterns = [
    path("",views.home),
    path('accesstoken/', views.get_access_token, name='get_access_token'),
    path('query/', views.query_stk_status, name='query_stk_status'),
    path('sellerlogin',views.sellerlogin,name='sellerlogin'),
    path("sellerhome",views.sellerhome, name="sellerhome"),
    path("sell",views.sell, name="sell"),
    path("customerdebit",views.customerdebit,name="customerdebit"),
]
