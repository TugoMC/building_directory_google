# portfolios/models.py
from django.db import models
from professionnels.models import Professionnel

class PortfolioImage(models.Model):
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='portfolio_images/', verbose_name="Image")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ['order']
        verbose_name = "Image du portfolio"
        verbose_name_plural = "Images du portfolio"

    def __str__(self):
        return f"Image {self.order} - {self.portfolio.title}"

class Portfolio(models.Model):
    professionnel = models.ForeignKey(
        Professionnel, 
        on_delete=models.CASCADE, 
        related_name='portfolios',
        verbose_name="Professionnel"
    )
    title = models.CharField(max_length=200, verbose_name="Titre du projet")
    description = models.TextField(verbose_name="Description du projet")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return f"{self.title} - {self.professionnel.full_name}"
