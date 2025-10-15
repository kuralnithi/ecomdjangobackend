from django.db import models
import bcrypt

class User(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]
    
    username = models.CharField(max_length=100, unique=True)
    emailid = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    usertype = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    resetPasswordToken = models.CharField(max_length=100, null=True, blank=True)
    resetPasswordTokenExpiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        
        
        
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True