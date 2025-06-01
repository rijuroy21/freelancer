from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Freelancer(models.Model):
    CATEGORY_CHOICES = [
        ("UI/UX & Web Designers", "UI/UX & Web Designers"),
        ("Graphic & Visual Designers", "Graphic & Visual Designers"),
        ("Digital & Marketing Designers", "Digital & Marketing Designers"),
        ("Multimedia & Video Designers", "Multimedia & Video Designers"),
        ("Industrial & Product Designers", "Industrial & Product Designers"),
    ]
    
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='freelancers')
    image = models.ImageField(upload_to='freelancer_images/', blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    bio = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subcategory}"


class WorkImage(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='work_images')
    image = models.ImageField(upload_to='work_samples/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image by {self.freelancer.name}"


class Review(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='reviews')
    client_name = models.CharField(max_length=255)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name}'s review for {self.freelancer.name}"