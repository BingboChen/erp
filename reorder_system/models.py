# erp/reorder_system/models.py

from django.db import models

class Fornitore(models.Model):
    id_fornitore_databricks = models.IntegerField(
        unique=True,
        blank=True,
        null=True,
        help_text="ID originale del fornitore da Databricks"
    )

    nome = models.CharField(max_length=255)
    indirizzo = models.CharField(max_length=255, blank=True, null=True)
    cap = models.CharField(max_length=20, blank=True, null=True)
    citta = models.CharField(max_length=100, blank=True, null=True)
    prov = models.CharField(max_length=100, blank=True, null=True)
    nazione = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=50, blank=True, null=True)
    cell = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    codicefiscale = models.CharField(max_length=50, blank=True, null=True)
    partitaiva = models.CharField(max_length=50, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    idata = models.DateTimeField(blank=True, null=True)
    paga = models.CharField(max_length=50, blank=True, null=True)
    ordinetot = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    minimo = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Fornitore"
        verbose_name_plural = "Fornitori"