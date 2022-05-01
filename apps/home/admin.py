from django.contrib import admin
from .models import Category,Tag,Project,Image,Comment,Reply,Rate,Comment_Report,Project_Report,Donation

# Register your models here.

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Project)
admin.site.register(Image)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Comment_Report)
admin.site.register(Project_Report)
admin.site.register(Donation)
admin.site.register(Rate)