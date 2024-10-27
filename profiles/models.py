# profiles/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
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