from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator
from datetime import datetime
from .generate_shareable_link import generate_shareable_link
from django.core.files.storage import default_storage

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=True)
    otp_expiry_time = models.DateTimeField(blank=True, null=True)
    passport = models.BinaryField(blank=True, null=True)
    health_card = models.BinaryField(blank=True, null=True)
    Visa = models.BinaryField(blank=True, null=True)
    PRcard = models.BinaryField(blank=True, null=True)
    trt = models.JSONField(default=list, blank=True)
    brt = models.JSONField(default=list, blank=True)
    total = models.JSONField(default=list, blank=True)


class AdditionalData(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)
    phone_no = models.CharField(max_length=20, blank=True)
    country_origin = models.CharField(max_length=100, blank=True)
    city_origin = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=6, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    facebook = models.CharField(max_length=100, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Trip(models.Model):
    trip_id = models.AutoField(primary_key=True)
    jwt_token = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_shared = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.jwt_token:
            self.jwt_token = generate_shareable_link()
        super(Trip, self).save(*args, **kwargs)

class SharedTrip(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)

    class Meta:
        unique_together = ('trip', 'email')
        
class Budget(models.Model):
    budget_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)

class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, validators=[MinLengthValidator(1)])
    type = models.CharField(max_length=15)
    date = models.DateField()
    quantity = models.DecimalField(max_digits=15, decimal_places=0)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'{self.budget.user} BudgetItem; {self.budget}'

    def make_list(self):
        return [self.description, self.type, self.date.strftime('%Y-%m-%d'), self.quantity, self.unit_cost]

class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

class CostEstimation(models.Model):
    estimation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    estimated_transportation_cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_accommodation_cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_activities_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateField(auto_now_add=True)

class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    login_dates = models.JSONField(default=dict)  

    def __str__(self):
        return self.user.username
    
class archivedTrips(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trips = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Archived Trips for {self.user.username}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    date = models.DateField()
    link = models.CharField(max_length=500)
    unread = models.BooleanField(default=True)

class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    body = models.CharField(max_length=20000)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

class BlogComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    comment = models.CharField(max_length=5000)
    likes = models.IntegerField(default=0)

class UserBlogLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, null=True)
    blog_comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE, null=True)

class City(models.Model):
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city}, {self.country}"