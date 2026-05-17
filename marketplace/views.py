from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .models import Product, Comment, Category
from .forms import ProductForm, CommentForm, RegisterForm


def home(request):
    products = Product.objects.filter(is_active=True).select_related('owner', 'category')
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    selected_category = request.GET.get('category', '')
    selected_sort = request.GET.get('sort', '')

    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if selected_category:
        products = products.filter(category_id=selected_category)
    if selected_sort == 'price_asc':
        products = products.order_by('price')
    elif selected_sort == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'marketplace/home.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': selected_category,
        'selected_sort': selected_sort,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    comments = product.comments.all().select_related('author')
    comment_form = CommentForm()
    return render(request, 'marketplace/product_detail.html', {
        'product': product,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            return redirect('marketplace:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'marketplace/create_product.html', {'form': form})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('marketplace:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/create_product.html', {'form': form, 'product': product, 'is_edit': True})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('marketplace:home')
    return render(request, 'marketplace/product_confirm_delete.html', {'product': product})


@login_required
def product_like(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user in product.likes.all():
        product.likes.remove(request.user)
    else:
        product.likes.add(request.user)
    return redirect('marketplace:product_detail', pk=pk)


@login_required
def add_comment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.author = request.user
            comment.save()
    return redirect('marketplace:product_detail', pk=pk)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('marketplace:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('marketplace:home')
    else:
        form = RegisterForm()
    return render(request, 'marketplace/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('marketplace:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next_url = request.GET.get('next') or 'marketplace:home'
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'marketplace/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('marketplace:home')
