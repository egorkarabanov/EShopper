from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='categories/%Y/%m/%d', blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:products_list_by_category', args=[self.slug])


class ProductSize(models.Model):
    size = models.CharField(max_length=101)

    def __str__(self):
        return self.size


class ProductColor(models.Model):
    color = models.CharField(max_length=100)

    def __str__(self):
        return self.color


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    size = models.ManyToManyField(ProductSize, related_name='products')
    color = models.ManyToManyField(ProductColor, related_name='products')

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail_view', args=[self.pk, self.slug])


class ProductPhoto(models.Model):
    photo = models.ImageField(upload_to='products_photo/%Y/%m/%d', blank=True)
    product = models.ForeignKey(Product, related_name='photos', on_delete=models.CASCADE)
