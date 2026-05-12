from django.shortcuts import render


def login(request):
    return render(request, 'core/login.html')


def signup(request):
    return render(request, 'core/signup.html')


def profile(request):
    user = {
        'username': 'JohnDoe',
        'email': 'john@example.com',
        'avatar': None,
    }
    return render(request, 'core/profile.html', {'user': user})
