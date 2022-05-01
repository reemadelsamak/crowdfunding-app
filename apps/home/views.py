
from asyncio.windows_events import NULL
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse


from apps.home.models import Category, Donation, Project
from apps.home.forms import Project_Form

from apps.authentication.models import Register


def getUser (request):
        user = Register.objects.get(id=request.session['user_id'])
        return user
    
   

def index(request):
        if 'user_id'  in request.session :
                user = getUser(request)
        else:
                user=NULL
        all_projects =Project.objects.all()
        last_5_projects = Project.objects.all().order_by('-id')[:5]
        
        context = {
                'segment': 'index',
                'all_projects' : all_projects,
                'count': len(all_projects),
                'last_5_projects' : last_5_projects,
                'user':user
                }
        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request))
        

def create_new_project(request):
        # if 'user_id' not in request.session :
        #      return  redirect('login')
        # else:
                if request.method == "POST":
                        form = Project_Form(request.POST)
                        if form.is_valid():
                                project = form.save()       
                                return redirect('home')
                else:
                        form = Project_Form()
                return render(request, "home/input-areas-forms.html", context={"form": form})




def show_project_details(request, project_id):
        if 'user_id' not in request.session :
             return  redirect('login')
        else:
                project = Project.objects.get(id=project_id)
                # relatedProjects = Project.objects.all().filter(category_id=project.category)
                context = {'project': project,
                        #    'relatedProjects': relatedProjects,
                        }
                return render(request, "home/project-details.html", context)



def donate(request, project_id):
        if 'user_id' not in request.session :
              return redirect('login')
        else:
                if request.method == "POST":
                        donation = Donation.objects.create(
                                Donation = request.POST['donate'],
                                project_id_id = project_id,
                                user_id_id = 1
                        )
                        return redirect('home') # handle to return to project details
                return render(request, "home/project-details.html")





def pages(request):
        if 'user_id' not in request.session :
              return redirect('login')
        else:
                context = {}
                        # All resource paths end in .html.
                        # Pick out the html file name from the url. And load that template.
                try : 
                        load_template = request.path.split('/')[-1]
                        if load_template == 'admin':
                                return HttpResponseRedirect(reverse('admin:index'))
                        context['segment'] = load_template

                        html_template = loader.get_template('home/' + load_template)
                        return HttpResponse(html_template.render(context, request))

                except template.TemplateDoesNotExist:

                        html_template = loader.get_template('home/page-404.html')
                        return HttpResponse(html_template.render(context, request))

