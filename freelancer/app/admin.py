from django.contrib import admin
from .models import Category, SubCategory, Freelancer
# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Freelancer)
