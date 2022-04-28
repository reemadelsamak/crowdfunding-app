from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse

from .forms import Project_Form

from apps.home.models import Category, Project
from apps.home.forms import Project_Form



@login_required(login_url="/login/")
def index(request):
    # return last 5 project
    all_projects =Project.objects.all()
    last_5_projects = Project.objects.all().order_by('-id')[:5]
    
    #return all Categories
    all_categories = Category.objects.all()

    context = {
            'segment': 'index',
            'all_projects' : all_projects,
            'count': len(all_projects),
            'last_5_projects' : last_5_projects,
            'all_categories' : all_categories
            }

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def create_new_project(request):

    if request.method == "POST":
        form = Project_Form(request.POST)

        if form.is_valid():
            project = form.save()       
            return redirect('home')
    else:
        form = Project_Form()
    return render(request, "home/input-areas-forms.html", context={"form": form})


@login_required(login_url="/login/")
def show_project_details(request):
    return render(request, "home/project-details.html")


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))



