from django.urls import path,include
from . import views

app_name = "inventory"

urlpatterns = [

    path('signup/', views.UserSignUpView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path("products/",views.ProductListView.as_view(),name="products"),
    path("products/create/",views.ProductCreateView.as_view(),name="create"),
    path('products/<int:pk>/', views.SaleCreateView.as_view(), name='saleCreate'),
    path('products/<int:pk>/delete', views.ProductDeleteView.as_view(), name='delete'),
    path('products/<int:pk>/update', views.ProductUpdateView.as_view(), name='update'),
    path('products/<int:pk>/purchase', views.PurchaseCreateView.as_view(), name='purchase'),
    path('products/<int:pk>/report', views.ProductTemplateView.as_view(), name='product_report'),
    path('products/Sale-report', views.SaleReport.as_view(), name='sale_report'),

    
]
