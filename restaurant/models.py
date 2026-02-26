from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Burger(models.Model):
    """Represents a menu item (burger) sold at the restaurant."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(blank=True, default='')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Feedback(models.Model):
    """Customer feedback / contact form submission."""
    # Nullable FK so guests (unauthenticated users) can also submit feedback
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks'
    )
    name = models.CharField(max_length=100)
    message = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name} ({self.rating}/5)"

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    """Extended profile information linked to the built-in User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Order(models.Model):
    """A placed order from a logged-in user."""
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('done',      'Done'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username} [{self.status}]"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """One line in an Order — a burger and how many were ordered."""
    order    = models.ForeignKey(Order,  on_delete=models.CASCADE, related_name='items')
    burger   = models.ForeignKey(Burger, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}× {self.burger.name}"

    @property
    def subtotal(self):
        return self.burger.price * self.quantity
