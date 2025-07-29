# erp/reorder_system/urls.py

from django.urls import path
from . import views # Importa le "views" della tua app corrente

app_name = 'reorder_system' # Definisci un namespace per gli URL della tua app

urlpatterns = [
    path('', views.home, name='home'),
    # Percorso per elencare tutti i fornitori
    path('fornitori/', views.fornitori_list, name='fornitori_list'),
    # Percorso per visualizzare i dettagli di un singolo fornitore (es. /fornitori/123/)
    path('fornitori/<int:pk>/', views.fornitore_detail, name='fornitore_detail'),
]