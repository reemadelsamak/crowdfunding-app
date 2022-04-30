from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=250)
    # category_icon = models.ImageField(upload_to='projects/static/projects')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=100)
    details = models.TextField()
    total_target = models.FloatField()
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    # image = models.ImageField(upload_to = "projects/static/projects")

    def __str__(self):
        return self.title
    


class Image(models.Model):
    image = models.ImageField(upload_to="projects/static/projects")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=None)


class Comment(models.Model):
    comment = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(f'comment by {self.user.name} on {self.project.title} project.')


class Donation(models.Model):
    donation = models.FloatField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # def __str__(self):
    #     return str(f'donated by {self.user.name} on {self.project.title} project.')


class Project_Report(models.Model):
    report = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment_Report(models.Model):
    report = models.TextField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Reply(models.Model):
    reply = models.TextField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Rate(models.Model):
    rate = models.IntegerField(default=1,
                                validators=[
                                    MaxValueValidator(5),
                                    MinValueValidator(1)
                                ])
    projcet = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
