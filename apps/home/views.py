# from asyncio.windows_events import NULL
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.db.models import Avg, Sum
from collections import defaultdict
from datetime import datetime
import re
from apps.home.models import Category, Comment, Donation, Project, Image, Project_Report, Rate, Reply, Tag, Comment_Report
from apps.home.forms import Project_Form, Report_form, Reply_form, Category_form
from django.forms.utils import ErrorList
from apps.authentication.models import Register
NULL={}

def getUser(request):
        user = Register.objects.get(id=request.session['user_id'])
        return user
    
def index(request):
    if 'user_id' in request.session:
        user = getUser(request)
    else:
        user = NULL
        
    highest_rated_projects = Project.objects.annotate(
       avg_rate=Avg('rate__rate')).order_by('-avg_rate')[:5]
    last_5_projects = Project.objects.all().order_by('-id')[:5]
    featured_projects = Project.objects.filter(is_featured=1)[:5]

    images = []
    for project in highest_rated_projects:
        images.append(project.image_set.all().first().images.url)

    context = {
        'highest_rated_projects':highest_rated_projects,
        'latest_5_projects': last_5_projects,
        'featured_projects': featured_projects,
        'images': images,
        'projects_count': len(Project.objects.all()),
        'donors_count': len(Donation.objects.all()),
        'reviews_count': len(Rate.objects.all()),
        'user': user
    }
    
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def create_new_project(request):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        my_images = Image.objects.all()
        if request.method == 'GET':

            form = Project_Form()
           
            
            return render(request, "home/create-project.html", context={"form": form, 'images': my_images, "user":user})

        if request.method == "POST":
            tag_error=''
                    
            if "tag" in request.POST or request.POST['newTag']!="":
                
                if(request.POST['newTag']!= ''):

                    newTag=re.sub("\s+","_",request.POST['newTag'].strip())
                    new_tag=Tag.objects.create(name=newTag).id
                    request.POST = request.POST.copy()
                    request.POST.update({
	                "tag":new_tag
                    })
            else:
                tag_error="Please add tag"
            
                    
            form = Project_Form(request.POST, request.FILES)
            if tag_error!="":
                
               form.add_error('tag',tag_error)
               
            images = request.FILES.getlist('images')
            if form.is_valid():
                project = form.save(commit=False)
                project.user = user
                project.save()
                form.save_m2m()
                for image in images:
                    Image.objects.create(project_id=project.id, images=image)
                return redirect('home')
        else:
            form = Project_Form()
        return render(request, "home/create-project.html", context={"form": form, "user":user})


def show_project_details(request, project_id):
    if 'user_id' not in request.session:
        user = NULL
    else:
        user = getUser(request)
    try:
        project = Project.objects.get(id=project_id)
        donate = project.donation_set.all().aggregate(Sum("donation"))
        donations_count = len(project.donation_set.all())
        comments = project.comment_set.all()
        replies = Reply.objects.all()
        project_images = project.image_set.all()
        counter=[]
        for image in project_images:
            counter.append("1")
        counter.pop()
        tags = project.tag.all()
        related_projects_tags = []
        for tag in tags:
            related_projects_tags.append(tag.project_set.all())

        related_projects = Project.objects.none().union(*related_projects_tags)[:4]
        related_projects_images = []
        for related_project in related_projects:
            related_projects_images.append(related_project.image_set.all().first().images.url)


        myFormat = "%Y-%m-%d %H:%M:%S"
        today = datetime.strptime(datetime.now().strftime(myFormat), myFormat)
        end_date = datetime.strptime(project.end_time.strftime(myFormat), myFormat)
        days_diff = (end_date-today).days
        
        new_report_form = Report_form()
        reply = Reply_form()

        donation_average = (donate["donation__sum"] if donate["donation__sum"] else 0)*100/project.total_target
        average_rating = project.rate_set.all().aggregate(Avg('rate'))['rate__avg']

        # return user rating if found
        user_rating = 0
        
        if 'user_id' in request.session:
            # prev_rating = Project.rate_set.get(user_id=user.id)
            prev_rating=[]

            if prev_rating:
                user_rating = prev_rating[0].rate

        if average_rating is None:
            average_rating = 0

        context = {
            'project': project,
            'donation': donate["donation__sum"] if donate["donation__sum"] else 0,
            'donations': donations_count,
            'days': days_diff,
            'comments': comments,
            'project_images': project_images,
            'replies': replies,
            'tags': tags,

            'report_form': new_report_form,
            'reply_form': reply,
            'related_projects': related_projects,
            'images': related_projects_images,
            
            'check_target': project.total_target*.25,
            'donation_average': donation_average,

            'rating': average_rating*20,
            'user_rating': user_rating,
            'rating_range': range(5, 0, -1),
            'average_rating': average_rating,
            
            'user':user,
            'counter':counter
            }

        return render(request, "home/project-details.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
 

def get_tag_projects(request, tag_id):
    if 'user_id' not in request.session:
        user = NULL
    else:
        user = getUser(request)
    context = {}
    try:
        tag = Tag.objects.get(id=tag_id)
        projects = tag.project_set.all()

        donations = []
        progress_values = []
        images = []
        for project in projects:
            donate = project.donation_set.all().aggregate(Sum("donation"))
            total_donation = donate["donation__sum"] if donate["donation__sum"] else 0
            
            progress_values.append(total_donation * 100/project.total_target)
            donations.append(total_donation)
            images.append(project.image_set.all().first().images.url)

        context = {
            'title': tag,
            'projects': projects,
            'images': images,
            'donations': donations,
            'progress_values': progress_values,
            'user':user
        }
        return render(request, "home/tag-projects.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def get_category_projects(request, category_id):
    if 'user_id' not in request.session:
        user = NULL
    else:
        user = getUser(request)
    context = {}
    try:
        projects = Project.objects.filter(
            category_id=category_id).all()

        donations = []
        progress_values = []
        images = []
        for project in projects:
            donate = project.donation_set.all().aggregate(Sum("donation"))
            total_donation = donate["donation__sum"] if donate["donation__sum"] else 0
            progress_values.append(total_donation * 100/project.total_target)

            donations.append(total_donation)

            images.append(project.image_set.all().first().images.url)

        title = Category.objects.get(id=category_id)
        context = {
            'title': title,
            'projects': projects,
            'donations': donations,
            'images': images,
            'progress_values': progress_values,
            'user':user
        }
        return render(request, "home/category.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def all_projects(request):
    if 'user_id' not in request.session:
        user = NULL
    else:
        user = getUser(request)
    context = {}
    try:
        projects = Project.objects.all()

        donations = []
        progress_values = []
        images = []
        for project in projects:
            donate = project.donation_set.all().aggregate(Sum("donation"))
            total_donation = donate["donation__sum"] if donate["donation__sum"] else 0
            progress_values.append(total_donation * 100/project.total_target)
            donations.append(total_donation)
            images.append(project.image_set.all().first().images.url)

        context = {
            'projects': projects,
            'images': images,
            'title': 'All Projects',
            'donations': donations,
            'progress_values': progress_values,
            'user':user
        }
        return render(request, "home/all_projects.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def get_featured_projects(request):
    if 'user_id' not in request.session:
        user = NULL
    else:
        user = getUser(request)
    context = {}
    try:
        projects = Project.objects.filter(is_featured=1).all()

        donations = []
        progress_values = []
        images = []
        for project in projects:
            donate = project.donation_set.all().aggregate(Sum("donation"))
            total_donation = donate["donation__sum"] if donate["donation__sum"] else 0
            progress_values.append(total_donation * 100/project.total_target)
            donations.append(total_donation)
            images.append(project.image_set.all().first().images.url)

        context = {
            'projects': projects,
            'images': images,
            'title': 'Featured Projects',
            'donations': donations,
            'progress_values': progress_values,
            'user':user
        }
        return render(request, "home/all_projects.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def donate(request, project_id):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        if request.method == "POST":
            if request.POST['donate']:
                donation = Donation.objects.create(
                    donation=request.POST['donate'],
                    project_id=project_id,
                    user_id=user.id,
                )
                return redirect('show_project', project_id)
        return render(request, "home/project-details.html", project_id , context={"user":user})


def create_comment(request, project_id):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        if request.method == "POST":
            if request.POST['comment']:
                comment = Comment.objects.create(
                    comment=request.POST['comment'],
                    project_id=project_id,
                    user_id=user.id
                )
                return redirect('show_project', project_id)
        return render(request, "home/project-details.html", project_id , context={"user":user})


def add_report(request, project_id):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        my_project = Project.objects.get(id=project_id)
        if request.method == "POST":
            Project_Report.objects.create(
                report='ip',
                project=my_project,
                user_id=user.id
            )
            return redirect('show_project', project_id)


def add_comment_report(request, comment_id):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        my_comment = Comment.objects.get(id=comment_id)
        project = Project.objects.all().filter(comment__id=comment_id)[0]

        if request.method == "POST":
            Comment_Report.objects.create(
                report='ip',
                comment=my_comment,
                user_id=user.id
            )
            return redirect('show_project', project.id)


def create_comment_reply(request, comment_id):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        if request.method == "POST":
            if request.POST['reply']:
                project = Project.objects.all().filter(comment__id=comment_id)[0]

                reply = Reply.objects.create(
                    reply=request.POST['reply'],
                    comment_id=comment_id,
                    user_id=user.id
                )
                return redirect('show_project', project.id)
        return render(request, "home/project-details.html", project.id)


def add_category(request):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        categories = Category.objects.all()

        if request.method == 'GET':
            form = Category_form()
            return render(request, "home/category_form.html", context={'form': form})
        if request.method == 'POST':
            form = Category_form(request.POST)

            if form.is_valid():
                new_category = request.POST['name']
                for category in categories:
                    if category.name == new_category:

                        error = ' not valid'

                        return render(request, "home/category_form.html", context={'form': form, 'form_error': error})

                form.save()
                return redirect('home')


def search(request):
    if 'user_id' not in request.session:
        user = NULL
    else:
        user = getUser(request)
    context = {}
    try:
        search_post = request.GET.get('search')

        if len(search_post.strip()) > 0:
            projects = Project.objects.filter(title__icontains=search_post)
            searched_tags = Tag.objects.filter(name__icontains=search_post)

            donations = []
            progress_values = []
            images = []
            for project in projects:
                donate = project.donation_set.all().aggregate(Sum("donation"))
                total_donation = donate["donation__sum"] if donate["donation__sum"] else 0

                progress_values.append(
                    total_donation * 100/project.total_target)
                donations.append(total_donation)
                images.append(project.image_set.all().first().images.url)

            context = {
                'projects': projects, 
                'tags': searched_tags, 
                'images': images,
                'donations': donations,
                'progress_values': progress_values,
                'user':user}

            if(len(projects) <= 0):
                context.update(
                    {'title': 'No Projects Found for "'+search_post+'"'})
            if(len(searched_tags) <= 0):
                context.update(
                    {'title_tags': 'No Tags Found for "'+search_post + '"'})

            return render(request, "home/search-result.html", context)
        else:
            return render(request, "home/index.html", context)

    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def rate(request, project_id):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        if request.method == "POST":
            project = get_object_or_404(Project, pk=project_id)
            context = {"project": project}

            rate = request.POST.get('rate', '')

            if rate and rate.isnumeric():

                apply_rating(project, user.id, rate)

        return redirect('show_project', project_id)


def apply_rating(project, user, rating):

    # If User rated the same project before --> change rate value
    prev_user_rating = project.rate_set.filter(user_id=user)
    if prev_user_rating:
        prev_user_rating[0].rate = int(rating)
        prev_user_rating[0].save()

    # first time to rate this project
    else:
        Rate.objects.create(
            rate=rating, projcet_id=project.id, user_id=user)


def cancel_project(request, project_id):
    if 'user_id' not in request.session:
        user = NULL
        return redirect('login')
    else:
        user = getUser(request)
        if request.method == 'POST':
            project = get_object_or_404(Project, pk=project_id)

            donate = project.donation_set.all().aggregate(Sum("donation"))
            donation = donate["donation__sum"] if donate["donation__sum"] else 0
            total_target = project.total_target
            
            if donation < total_target*.25:
                project.delete()
                return redirect("profile")
            else:
                return redirect('show_project', project_id)
                
           

def pages(request):  
    if 'user_id' not in request.session:
        user = NULL
    else:
        user = getUser(request)     
    context = {}
    try : 
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
                return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        context['user'] = user

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
            html_template = loader.get_template('home/page-404.html')
            return HttpResponse(html_template.render(context, request))
