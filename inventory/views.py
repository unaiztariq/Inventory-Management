
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView,LogoutView, PasswordChangeView
from django.views.generic import ListView,CreateView,DetailView,UpdateView,FormView,View,DeleteView,TemplateView
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.urls  import reverse_lazy,reverse

from .models import Product,Sale,Purchase
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum,Count,Q
# Create your views here.


class UserLoginView(LoginView):
    template_name= "inventory\login.html"

    def get_success_url(self):
        return reverse("inventory:products")
    def get_initial(self):
        initial =super().get_initial() 
        initial["username"]="EnterName"
        return initial
    
class UserSignUpView(FormView):
    template_name = "inventory/signup.html"
    form_class = UserCreationForm
    
    def get_success_url(self):
        return reverse_lazy("inventory:products")
    
    def form_valid(self, form):
        user = form.save()  
        login(self.request,user)        
        return super().form_valid(form)

class UserLogoutView(LogoutView):
    next_page = reverse_lazy("inventory:login")


class ProductCreateView(LoginRequiredMixin,CreateView):
    model= Product
    template_name ="inventory/create.html"
    fields=["name","price"]
    success_url= reverse_lazy("inventory:products")

    def form_valid(self, form):
        
        form.instance.user = self.request.user
        return super().form_valid(form)
    


class ProductListView(LoginRequiredMixin,ListView):

    model = Product
    template_name = "inventory\product.html"
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context["total_products"] = Product.objects.all().count()
        context["total_purchases"] = Purchase.objects.all().count()
        context["total_sales"] = Sale.objects.all().count()
        # stock = Product.objects.aggregate(total = Sum("stock",default =0))
        products = Product.objects.all()
        stock = 0
        for product in products:
            stock+= product.price*product.stock
        context["total_stocks"] = stock
        return context    
    
    def get_ordering(self):
        order = self.request.GET.get("sort","-updated_at")
        return order
    
    def get_queryset(self): 
        user = self.request.user 
        exp_lsit= Product.objects.all() 
        ordering = self.get_ordering()
        return exp_lsit.order_by(ordering)

class ProductDeleteView(LoginRequiredMixin,DeleteView):
    model = Product
    template_name= "inventory\delete.html"
    success_url = reverse_lazy("inventory:products")
    context_object_name = "product"

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        product = Product.objects.get(id=pk)
        if self.request.user != product.user:
            return redirect('inventory:products')
        return super().get(request, *args, **kwargs)

# class ProductDetailView(LoginRequiredMixin,DetailView):
#     model= Product
#     context_object_name = "product"
#     def get_template_names(self):
#         pk = self.kwargs['pk']
#         product = Product.objects.get(id=pk)
#         if self.request.user == product.user:
#             return ['inventory/detailuser.html']
#         return ['inventory/detail.html']

class SaleCreateView(LoginRequiredMixin,CreateView):
    model= Sale
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        pk = self.kwargs['pk']              
        product = Product.objects.get(id=pk)
        context["product"]= product
        return context
        
    def get_template_names(self):
        pk = self.kwargs['pk']
        product = Product.objects.get(id=pk)
        if self.request.user == product.user:
            return ['inventory/detailuser.html']
        return ['inventory/detail.html']    
    
    fields = ["quantity"]
    success_url= reverse_lazy("inventory:products")
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        pk = self.kwargs['pk']
        product = Product.objects.get(id=pk)
        form.instance.product = product
        form.instance.user = self.request.user
        return form
        


    def form_valid(self, form):
        pk = self.kwargs['pk']
        product = Product.objects.get(id=pk)
        Product.objects.filter(id=product.id).update(stock=product.stock-form.instance.quantity)
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin,UpdateView):
    model=Product
    template_name = "inventory\productupdate.html"

    fields=["name","price","stock"]
    success_url = reverse_lazy("inventory:products")

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        product = Product.objects.get(id=pk)
        if self.request.user != product.user:
            return redirect('inventory:products')
        return super().get(request, *args, **kwargs)
    



class PurchaseCreateView(LoginRequiredMixin,CreateView):
    model= Purchase
    template_name ="inventory/purchase_create.html"
    fields=["quantity"]
    success_url= reverse_lazy("inventory:products")

    def get_context_data(self, **kwargs):

        context =super().get_context_data(**kwargs)
        products = Product.objects.filter(user=self.request.user)
        context["products"]=products

        return context
    
    def get_form(self, form_class = None):
        form = form = super().get_form(form_class) # get form class does'nt work here 
        # it function just looks at your view's `form_class` attribute and returns it — or builds one 
        # automatically from your model if you didn't set `form_class`.

        form.instance.user_id = self.request.user.id
        try:
            product_id = self.request.POST.get("product")
            if product_id:
                    form.instance.product = Product.objects.get(id=product_id)
        except (ValueError, Product.DoesNotExist):
                form.add_error("quantity", "Please select a Product first.")

        return form
            
    
    

    def form_valid(self, form):
        try:
            product_id = self.request.POST.get("product")
            stock = Product.objects.get(id=product_id).stock
        except (Product.DoesNotExist,ValueError):
            form.add_error("quantity", "Please select a Product first.")
            return self.form_invalid(form)
    
        Product.objects.filter(id=product_id).update(stock =stock+form.instance.quantity)
        return super().form_valid(form)
    


    # get_form(form_class)
    # └── calls get_form_class()  ← figures out WHICH class to use
    #         └── returns the class (e.g. PurchaseForm)
    # └── then instantiates it with POST data, instance, prefix, etc.
    # └── returns the actual form object
    
    


class ProductTemplateView(LoginRequiredMixin,TemplateView):
    
    template_name ="inventory/product_report.html"
    

    def get_context_data(self, **kwargs): 
        product_id = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        product=Product.objects.filter(id=product_id)
        
        context["product"]= Product.objects.get(id=product_id)

        purchase = product.aggregate(purchased= Count("purchase"))
        context['purchased'] = purchase["purchased"]
        sale = product.aggregate(sold= Count("sale"))
        context['sold'] = sale["sold"]
        context['remaining'] = purchase["purchased"]-sale["sold"]
        return context 


from django.views.generic.base import TemplateResponseMixin, ContextMixin

class SaleReport(TemplateResponseMixin,ContextMixin,View):
    template_name="inventory/sale_report.html"
    def get_context_data(self, month=None,  error=None,**kwargs):
        context = super().get_context_data(**kwargs)
        sales = Sale.objects.all()  

        context["products"] = Product.objects.annotate(total=Sum("sale__total_amount", default=0))
        if month :
            context["month"]= month
            month = int(month.split("-")[1])
        
            sales = sales.filter(date__month=month)
            context["products"] = Product.objects.annotate(total=Sum("sale__total_amount",filter= Q(sale__date__month=month), default=0))

        context["total"] = sales.aggregate(total=Sum("total_amount", default=0))["total"]
       
        if error:
            context["error"] = error

        return context
    

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        month = request.POST.get("salemonth")
        if month is "":
            context = self.get_context_data(error="Please select a month first")
            return self.render_to_response(context)
        
        context = self.get_context_data(month=month)
        return self.render_to_response(context)
    
    



