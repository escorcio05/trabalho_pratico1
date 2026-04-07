from django.db import models

class Genero(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

class Realizador(models.Model):
    nome = models.CharField(max_length=70)

    def __str__(self):
        return self.nome

class Ator(models.Model):
    nome = models.CharField(max_length=70)

    def __str__(self):
        return self.nome

class Filme(models.Model):
    titulo = models.CharField(max_length=100)
    data_lancamento = models.DateField()
    sinopse = models.TextField(blank=True, null=True)
    cartaz = models.URLField(max_length=500, null=True, blank=True)
    realizador = models.ForeignKey(Realizador, on_delete=models.CASCADE)
    atores = models.ManyToManyField(Ator)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo