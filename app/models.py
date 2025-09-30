from django.db import models
from django.contrib.auth.models import User

# cloudinary
from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage, uploader


# Create your models here.
class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id} - {self.title}'



class ProfileImage(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile_image")
    image_url = models.URLField(max_length=500, blank=True, null=True)


    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} Profile Image"