# erp/reorder_system/views.py

from django.shortcuts import render, get_object_or_404
from .models import Fornitore # Importa il tuo modello Fornitore

def home(request):
    """
    Vista per la pagina iniziale (home page) dell'applicazione.
    """
    return render(request, 'reorder_system/home.html') # Renderizza il template home.html

def fornitori_list(request):
    """
    Vista per elencare tutti i fornitori.
    """
    fornitori = Fornitore.objects.all().order_by('nome') # Recupera tutti i fornitori, ordinati per nome
    context = {
        'fornitori': fornitori
    }
    return render(request, 'reorder_system/fornitori_list.html', context)

def fornitore_detail(request, pk):
    """
    Vista per visualizzare i dettagli di un singolo fornitore.
    """
    # Recupera il fornitore tramite la sua Primary Key (pk)
    fornitore = get_object_or_404(Fornitore, pk=pk)
    context = {
        'fornitore': fornitore
    }
    return render(request, 'reorder_system/fornitore_detail.html', context)