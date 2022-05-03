from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.db.models import Avg, Sum
from django.db.models import Q

from datetime import datetime

from apps.home.models import Category, Comment, Donation, Project, Image, Project_Report, Rate, Reply, Tag, User, Comment_Report
from apps.home.forms import Project_Form, Report_form, Reply_form, Category_form


@login_required(login_url="/login/")
def index(request):
    all_projects = Project.objects.all()
    last_5_projects = Project.objects.all().order_by('-id')[:5]
    featured_projects = Project.objects.filter(is_featured=1)[:5]
    donations = Donation.objects.all()
    reviews = Rate.objects.all()

    images = []
    for project in last_5_projects:
        images.append(project.image_set.all().first())

    context = {
        'segment': 'index',
        'all_projects': all_projects,
        'count': len(all_projects),
        'last_5_projects': last_5_projects,
        'featured_projects': featured_projects,
        'images': images,
        'donors': len(donations),
        'reviews': len(reviews)
    }

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def create_new_project(request):
    my_images = Image.objects.all()
    if request.method == 'GET':

        form = Project_Form()
        return render(request, "home/create-project.html", context={"form": form, 'images': my_images})

    if request.method == "POST":
        form = Project_Form(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        if form.is_valid():
            project = form.save()
            for image in images:
                Image.objects.create(project_id=project.id, images=image)
            return redirect('home')
    else:
        form = Project_Form()
    return render(request, "home/create-project.html", context={"form": form})


@login_required(login_url="/login/")
def show_project_details(request, project_id):

    context = {}
    try:
        project = Project.objects.get(id=project_id)
        donate = project.donation_set.all().aggregate(Sum("donation"))
        donations = len(project.donation_set.all())
        comments = project.comment_set.all()
        replies = Reply.objects.all()

        project_images = project.image_set.all()
        tags = project.tag.all()

        related_projects_tags = []
        for tag in tags:
            related_projects_tags.append(tag.project_set.all())

        related_projects = Project.objects.none().union(
            *related_projects_tags)[:4]

        related_projects_images = []
        for project in related_projects:
            related_projects_images.append(project.image_set.all().first())

        myFormat = "%Y-%m-%d %H:%M:%S"
        today = datetime.strptime(datetime.now().strftime(myFormat), myFormat)
        start_date = datetime.strptime(
            project.start_time.strftime(myFormat), myFormat)
        end_date = datetime.strptime(
            project.end_time.strftime(myFormat), myFormat)
        days_diff = (end_date-today).days
        new_report_form = Report_form()
        reply = Reply_form()

        donation_average = (
            donate["donation__sum"] if donate["donation__sum"] else 0)*100/project.total_target

        average_rating = project.rate_set.all().aggregate(Avg('rate'))[
            'rate__avg']

        # return user rating if found
        user_rating = 0

        if request.user.is_authenticated:
            # prev_rating = Project.rate_set.filter(user_id=1)
            prev_rating = []

            if prev_rating:
                user_rating = prev_rating[0].value

        if average_rating is None:
            average_rating = 0

        context = {'project': project,
                   'donation': donate["donation__sum"] if donate["donation__sum"] else 0,
                   'donations': donations,
                   'days': days_diff,
                   'comments': comments,
                   'num_of_comments': len(comments),
                   'project_images': project_images,
                   'replies': replies,
                   'tags': tags,

                   'report_form': new_report_form,
                   'reply_form': reply,
                   'related_projects': related_projects,
                   'images': related_projects_images,

                   'donation_average': donation_average,

                   'rating': average_rating*20,
                   'user_rating': user_rating,
                   'rating_range': range(5, 0, -1),
                   'average_rating': average_rating,
                   }

        return render(request, "home/project-details.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def get_tag_projects(request, tag_id):
    context = {}
    try:
        tag = Tag.objects.get(id=tag_id)
        projects = tag.project_set.all()

        images = []
        for project in projects:
            images.append(project.image_set.all().first())

        context = {
            'title': tag,
            'projects': projects,
            'images': images
        }
        return render(request, "home/tag-projects.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def get_category_projects(request, category_id):
    context = {}
    try:
        projects = Project.objects.filter(
            category_id=category_id).all()

        images = []
        donations = []
        for project in projects:
            donate = project.donation_set.all().aggregate(Sum("donation"))
            test = donate["donation__sum"] if donate["donation__sum"] else 0
            donations.append(test)

            images.append(project.image_set.all().first())

        title = Category.objects.get(id=category_id)
        context = {
            'title': title,
            'projects': projects,
            'donations': donations,
            'images': images,
        }
        return render(request, "home/category.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def all_projects(request):
    context = {}
    try:
        projects = Project.objects.all()

        images = []
        for project in projects:
            donate = project.donation_set.all().aggregate(Sum("donation"))
            images.append(project.image_set.all().first())

        context = {
            'projects': projects,
            'donation': donate["donation__sum"] if donate["donation__sum"] else 0,
            'images': images,
            'title': 'All Projects'
        }
        return render(request, "home/all_projects.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def get_featured_projects(request):
    context = {}
    try:
        projects = Project.objects.filter(is_featured=1).all()

        images = []
        for project in projects:
            donate = project.donation_set.all().aggregate(Sum("donation"))
            images.append(project.image_set.all().first())

        context = {
            'projects': projects,
            'donation': donate["donation__sum"] if donate["donation__sum"] else 0,
            'images': images,
            'title': 'Featured Projects'
        }
        return render(request, "home/all_projects.html", context)
    except Project.DoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def donate(request, project_id):
    if request.method == "POST":
        if request.POST['donate']:
            donation = Donation.objects.create(
                donation=request.POST['donate'],
                project_id=project_id,
                user_id=1
            )
            # handle to return to project details
            return redirect('show_project', project_id)
    return render(request, "home/project-details.html", project_id)


@login_required(login_url="/login/")
def create_comment(request, project_id):
    if request.method == "POST":
        if request.POST['comment']:
            comment = Comment.objects.create(
                comment=request.POST['comment'],
                project_id=project_id,
                user_id=1
            )
            # handle to return to project details
            return redirect('show_project', project_id)
    return render(request, "home/project-details.html", project_id)


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


@login_required(login_url="/login/")
def add_report(request, project_id):
    my_project = Project.objects.get(id=project_id)
    if request.method == "POST":
        # myuser_id=request.user.id
        # check=User.objects.get(id=1).project_report_set.all().id
        # print(check)

        Project_Report.objects.create(
            report='ip',
            project=my_project,
            # user_id = request.user.id
            user_id=1
        )
        # handle to return to project details
        return redirect('show_project', project_id)


@login_required(login_url="/login/")
def add_comment_report(request, comment_id):
    my_comment = Comment.objects.get(id=comment_id)
    project = Project.objects.all().filter(comment__id=comment_id)[0]

    if request.method == "POST":
        # myuser_id=request.user.id
        # check=User.objects.get(id=1).project_report_set.all().id
        # print(check)

        Comment_Report.objects.create(
            report='ip',
            comment=my_comment,
            # user_id = request.user.id
            user_id=1
        )
        # handle to return to project details
        return redirect('show_project', project.id)


@login_required(login_url="/login/")
def create_comment_reply(request, comment_id):

    if request.method == "POST":
        if request.POST['reply']:
            project = Project.objects.all().filter(comment__id=comment_id)[0]

            reply = Reply.objects.create(
                reply=request.POST['reply'],
                comment_id=comment_id,
                # user_id = request.user.id
                user_id=1
            )

            # handle to return to project details
            return redirect('show_project', project.id)
    return render(request, "home/project-details.html", project.id)


@login_required(login_url="/login/")
def add_category(request):

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
    context = {}
    try:
        search_post = request.GET.get('search')

        if len(search_post.strip()) > 0:
            projects = Project.objects.filter(title__icontains=search_post)
            searched_tags = Tag.objects.filter(name__icontains=search_post)

            context = {'projects': projects, 'tags': searched_tags}

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

    if request.method == "POST":
        project = get_object_or_404(Project, pk=project_id)
        context = {"project": project}

        rate = request.POST.get('rate', '')

        if rate and rate.isnumeric():

            apply_rating(project, 1, rate)

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
