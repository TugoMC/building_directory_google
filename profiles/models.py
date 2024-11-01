from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added

class Profile(models.Model):
    PROFESSION_CHOICES = [
        ('STUDENT', 'Étudiant'),
        ('TEACHER', 'Enseignant'),
        ('ENGINEER', 'Ingénieur'),
        ('DOCTOR', 'Médecin'),
        ('OTHER', 'Autre'),
    ]
    
    CITY_CHOICES = [
        ('PARIS', 'Paris'),
        ('LYON', 'Lyon'),
        ('MARSEILLE', 'Marseille'),
        ('TOULOUSE', 'Toulouse'),
        ('BORDEAUX', 'Bordeaux'),
    ]
    
    COMMUNE_CHOICES = [
        ('PARIS', 'Paris'),
        ('LYON', 'Lyon'),
        ('MARSEILLE', 'Marseille'),
        ('TOULOUSE', 'Toulouse'),
        ('BORDEAUX', 'Bordeaux'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField("Prénom", max_length=50, blank=True)
    last_name = models.CharField("Nom", max_length=50, blank=True)
    profession = models.CharField("Profession", max_length=20, choices=PROFESSION_CHOICES, blank=True)
    city = models.CharField("Ville", max_length=20, choices=CITY_CHOICES, blank=True)
    commune = models.CharField("Commune", max_length=20, choices=COMMUNE_CHOICES, blank=True)
    profile_image = models.ImageField(
        "Photo de profil",
        upload_to='profile_images/',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f"{self.user.email}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(user_signed_up)
def create_profile_on_signup(request, user, **kwargs):
    Profile.objects.get_or_create(user=user)

@receiver(social_account_added)
def create_profile_on_social_added(request, sociallogin, **kwargs):
    Profile.objects.get_or_create(user=sociallogin.user)