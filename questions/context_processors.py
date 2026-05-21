from .models import Tag
from django.contrib.auth.models import User


def sidebar(request):
    return {
        'tags': Tag.objects.order_by('name')[:20],
        'best_members': User.objects.order_by('-date_joined').select_related('profile')[:5],
    }
