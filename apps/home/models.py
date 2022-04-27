from django.db import models
from django.contrib.auth.models import User

from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=250)

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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to = "projects/static/projects")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    tag_id = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title


class Image(models.Model):
    image = models.ImageField(upload_to="projects/static/projects")
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)

    

class Comment(models.Model):
    comment = models.TextField()
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Reply(models.Model):
    reply = models.TextField()
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment_Report(models.Model):
    report = models.TextField()
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Project_Report(models.Model):
    report = models.TextField()
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Donation(models.Model):
    Donation = models.FloatField()
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Rate(models.Model):
    rate = models.CharField(max_length=100, choices=[(
        '1', '1star'), ('2', '2stars'), ('3', '3stars'), ('4', '4stars'), ('5', '5stars')], default='3')
    projcet_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
