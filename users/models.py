from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, emailid, username, password=None, **extra_fields):
        if not emailid:
            raise ValueError("Email is required")
        emailid = self.normalize_email(emailid)
        user = self.model(emailid=emailid, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, emailid, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(emailid, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    emailid = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    usertype = models.CharField(max_length=20, choices=[('customer','Customer'),('admin','Admin')], default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resetPasswordToken = models.CharField(max_length=100, null=True, blank=True)
    resetPasswordTokenExpiry = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'emailid'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        db_table = 'users'
