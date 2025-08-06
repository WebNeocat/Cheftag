from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('super:home')  # Redirige a superadmin si es superusuario
            return redirect('alimentos:home')  # Redirige a la página normal si no es superusuario
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login/login.html')

def logout_view(request):
    logout(request)
    return redirect('login:login')
