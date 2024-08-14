"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import *
urlpatterns = [
    path("admin/", admin.site.urls),
    path("",login,name="login"),
    path("dashboard/",home,name="adminHome"),
    path("home/",employeeHome,name="employeeHome"),
    path("customer/",customers,name="customer"),
    path("employee/",employees,name="employee"),
    path("vendor/",vendors,name="vendor"),
    path("products/",products,name="products"),
    path("purchase/",purchase,name="purchase"),
    path("sales/",sales,name="sales"),
    path("purchaseReports/",purchaseReports,name="purchaseReports"),
    path("salesReports/",salesReports,name="salesReports"),
    path("productReports/",productReports,name="productReports"),
    path("productReStock/",productReStock,name="productReStock")
    
]
