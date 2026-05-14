from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    image_url = models.URLField()

    def __str__(self): return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('Yangi', 'Yangi'),
        ('O\'lchanmoqda', 'O\'lchanmoqda'),
        ('Jarayonda', 'Jarayonda'),
        ('O\'rnatilmoqda', 'O\'rnatilmoqda'),
        ('Tugatildi', 'Tugatildi'),
    ]
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    service_type = models.CharField(max_length=100) # Masalan: Darvoza, Panjara
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Yangi')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Master(models.Model):
    full_name = models.CharField(max_length=255)
    occupation = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)