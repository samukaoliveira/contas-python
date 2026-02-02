# controle_gastos/views/errors.py
from django.shortcuts import render

def erro_404(request, exception):
    return render(request, "errors/404.html", status=404)

def erro_500(request):
    return render(request, "errors/500.html", status=500)
