from apps.home.models import Category

def show_category(request):
    return {'all_categories' : Category.objects.all()}
