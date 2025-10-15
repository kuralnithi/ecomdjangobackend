from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    ratings = models.DecimalField(max_digits=3, decimal_places=2)
    image = models.CharField(max_length=500, blank=True)
    category = models.CharField(max_length=100)
    seller = models.CharField(max_length=100)
    stock = models.IntegerField()
    numOfReviews = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'