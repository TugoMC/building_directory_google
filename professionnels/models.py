from django.db import models


class Professionnel(models.Model):
    # Informations personnelles
    full_name = models.CharField(max_length=255, verbose_name="Nom complet")
    profile_photo = models.ImageField(
        upload_to="photos/", null=True, blank=True, verbose_name="Photo de profil"
    )
    email = models.EmailField(unique=True, verbose_name="Email", db_index=True)
    phone = models.CharField(max_length=20, verbose_name="Téléphone", db_index=True)

    CITY_CHOICES = [
        ("Abidjan", "Abidjan"),
        ("Yamoussoukro", "Yamoussoukro"),
        # Ajoutez d'autres villes ici...
    ]
    city = models.CharField(max_length=100, choices=CITY_CHOICES, verbose_name="Ville")

    COMMUNE_CHOICES = [
        ("Abobo", "Abobo"),
        ("Adjamé", "Adjamé"),
        # Ajoutez d'autres communes ici...
    ]
    commune = models.CharField(
        max_length=100, choices=COMMUNE_CHOICES, verbose_name="Commune"
    )

    presentation_video = models.FileField(
        upload_to="videos/", null=True, blank=True, verbose_name="Vidéo de présentation"
    )

    # Caractéristiques professionnelles
    SPECIALIZATIONS = [
        ("Gros Oeuvre", "Gros Oeuvre"),
        ("Second Oeuvre", "Second Oeuvre"),
        # Ajoutez d'autres spécialisations ici...
    ]
    specialization = models.CharField(
        max_length=255, choices=SPECIALIZATIONS, verbose_name="Spécialisation"
    )

    class SkillLevel(models.TextChoices):
        DEBUTANT = "Débutant", "Débutant"
        INTERMEDIAIRE = "Intermédiaire", "Intermédiaire"
        EXPERT = "Expert", "Expert"

    skill_level = models.CharField(
        max_length=50,
        choices=SkillLevel.choices,
        verbose_name="Niveau de compétence",
    )

    certifications = models.TextField(verbose_name="Certifications", blank=True)
    years_of_experience = models.PositiveIntegerField(
        help_text="Nombre d'années d'expérience", verbose_name="Années d'expérience"
    )
    daily_rate = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Tarif journalier"
    )
    
    availability = models.CharField(
        max_length=255,
        help_text="Exemple : Lundi,Mardi,Mercredi",
        verbose_name="Disponibilité",
    )

    # Méthode pour récupérer la disponibilité sous forme de liste
    def get_workdays_list(self):
        return self.availability.split(",") if self.availability else []
    

    def __str__(self):
        return self.full_name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
        ]
