import uuid
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import Field

class PostgreSQLEnumField(Field):
    def __init__(self, enum_name, *args, **kwargs):
        self.enum_name = enum_name  # Store ENUM type name
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        """Return the ENUM type name as the column type in PostgreSQL."""
        return self.enum_name

    def deconstruct(self):
        """Ensure Django migrations can serialize this field properly."""
        name, path, args, kwargs = super().deconstruct()
        kwargs["enum_name"] = self.enum_name
        return name, path, args, kwargs

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)

class User(AbstractBaseUser, BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    add1 = models.CharField("Address Line 1", max_length=255)
    add2 = models.CharField("Address Line 2", max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    state = models.CharField(max_length=100)
    countryCode = models.CharField(max_length=10)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'user'

class Category(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'Categories'

class Product(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product', db_column='userId')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product', db_column='categoryId')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    unit = PostgreSQLEnumField('unit', default='pcs')
    deleted = models.BooleanField(default=False)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'product'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['deleted']),
        ]

class Inventory(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory',db_column='productId')
    quantity = models.PositiveIntegerField()
    reorderLevel = models.PositiveIntegerField(default=10)

    class Meta:
        db_table = 'inventory'
    
class ChatHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatHistory', db_column='userId')
    threadId = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'chatHistory'

