from django.shortcuts import render, get_object_or_404, HttpResponse
from .models import Category, Product, ProductColor, ProductSize
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.template.loader import render_to_string
from utils.ajax import is_ajax
from like.like import Like


def home(request):
    products = Product.objects.all().order_by('-updated')
    categories = Category.objects.all()
    categories_with_images = [category for category in categories if category.image]
    return render(request, 'shop/home.html', {'products': products, 'page': 'home',
                                              'category_img': categories_with_images})


class ProductsListView(ListView):
    model = Product
    template_name = 'shop/list.html'
    queryset = Product.objects.all()
    paginate_by = 9

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = Product.objects.filter(category__slug=category_slug)
        else:
            queryset = super().get_queryset()

        order_by = self.request.GET.get('order_by')
        if order_by:
            if order_by == 'latest':
                queryset = queryset.order_by('-created')
            if order_by == 'cheap':
                queryset = queryset.order_by('price')
            if order_by == 'expansive':
                queryset = queryset.order_by('-price')

        size_name = self.request.GET.get('size')
        color_name = self.request.GET.get('color')

        if size_name and color_name:
            size_names = size_name.split('_')
            color_names = color_name.split('_')

            queryset = queryset.filter(
                Q(size__size__in=size_names) & Q(color__color__in=color_names)
            )
        elif size_name:
            size_names = size_name.split('_')
            queryset = queryset.filter(size__size__in=size_names)
        elif color_name:
            color_names = color_name.split('_')
            queryset = queryset.filter(color__color__in=color_names)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            colors = ProductColor.objects.annotate(
                count=Count('products', filter=Q(products__category__slug=category_slug)))
            sizes = ProductSize.objects.annotate(
                count=Count('products', filter=Q(products__category__slug=category_slug)))
        else:
            colors = ProductColor.objects.annotate(count=Count('products'))
            sizes = ProductSize.objects.annotate(count=Count('products'))
        context['colors'] = colors
        context['sizes'] = sizes

        return context

    def render_to_response(self, context, **response_kwargs):
        if is_ajax(self.request):
            like = Like(self.request)
            context.update({'like': like})
            return HttpResponse(render_to_string('shop/frames/product_list.html', context))
        return super().render_to_response(context, **response_kwargs)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/detail.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recommended_products'] = Product.objects.all()[:5]
        return context
