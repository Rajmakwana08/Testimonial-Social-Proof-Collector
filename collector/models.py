from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_username()


class Space(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="spaces")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True)
    logo = models.ImageField(upload_to="space_logos/", blank=True, null=True)
    prompt = models.CharField(max_length=240, default="What did you enjoy most about working with us?")
    require_avatar = models.BooleanField(default=False)
    enable_ratings = models.BooleanField(default=True)
    custom_questions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        ARCHIVED = "archived", "Archived"

    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="testimonials")
    client_name = models.CharField(max_length=100)
    email = models.EmailField()
    company_role = models.CharField(max_length=140, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    message = models.TextField(max_length=2000)
    avatar = models.ImageField(upload_to="testimonial_avatars/", blank=True, null=True)
    answers = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    is_featured = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.client_name} - {self.space.name}"
