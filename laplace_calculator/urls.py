from django.urls import path
from . import views

app_name = 'laplace_calculator'
urlpatterns = [
    path('', views.calculator, name='calculator'),  # Modo calculadora
    path('graph/', views.graph, name='graph'),      # Modo solo gráficas
]