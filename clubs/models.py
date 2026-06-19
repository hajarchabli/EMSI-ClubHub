from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Etudiant"
        CLUB_MANAGER = "club_manager", "Responsable de club"
        ADMINISTRATION = "administration", "Administration"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    filiere = models.CharField(max_length=100, blank=True, null=True, verbose_name="Filière")

    def max_joinable_clubs(self):
        if self.role == self.Role.CLUB_MANAGER:
            return 2
        return 3

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})".strip()


class Club(models.Model):
    class Category(models.TextChoices):
        MUSIQUE = "Musique", "Musique"
        TECH = "Tech & Innovation", "Tech & Innovation"
        SPORTS = "Sports", "Sports"
        ARTS = "Arts", "Arts"
        AUTRE = "Autre", "Autre"

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.AUTRE)
    logo = models.ImageField(upload_to="club_logos/", blank=True, null=True)
    manager = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="managed_club",
        limit_choices_to={"role": User.Role.CLUB_MANAGER},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ClubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="club_memberships")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "club")

    def clean(self):
        if self.user.role == User.Role.ADMINISTRATION:
            raise ValidationError("L'administration ne peut pas etre membre d'un club.")
        current_count = ClubMembership.objects.filter(user=self.user).exclude(pk=self.pk).count()
        if current_count >= self.user.max_joinable_clubs():
            raise ValidationError("Limite de clubs atteinte pour cet utilisateur.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} -> {self.club.name}"


class ClubJoinRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        APPROVED = "approved", "Acceptee"
        REJECTED = "rejected", "Rejetee"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="club_join_requests")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="join_requests")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "club")

    def __str__(self):
        return f"Demande {self.user.username} -> {self.club.name}"


class ClubCreationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        APPROVED = "approved", "Acceptee"
        REJECTED = "rejected", "Rejetee"

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="club_creation_requests")
    club_name = models.CharField(max_length=120)
    description = models.TextField()
    logo = models.ImageField(upload_to="club_creation_logos/")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Creation club: {self.club_name}"


class Event(models.Model):
    class Location(models.TextChoices):
        SALLE_12 = "Salle 12", "Salle 12"
        SALLE_22 = "Salle 22", "Salle 22"
        SALLE_35 = "Salle 35", "Salle 35"
        AMPHI = "Amphithéâtre", "Amphithéâtre"
        SOCIOCULTURELLE = "Salle Socioculturelle", "Salle Socioculturelle"

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=150)
    description = models.TextField()
    event_date = models.DateField()
    event_time = models.TimeField(null=True, blank=True, verbose_name="Heure")
    location = models.CharField(
        max_length=50,
        choices=Location.choices,
        default=Location.SALLE_12,
        verbose_name="Lieu",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.club.name})"


class EventRequest(models.Model):
    class Location(models.TextChoices):
        SALLE_12 = "Salle 12", "Salle 12"
        SALLE_22 = "Salle 22", "Salle 22"
        SALLE_35 = "Salle 35", "Salle 35"
        AMPHI = "Amphithéâtre", "Amphithéâtre"
        SOCIOCULTURELLE = "Salle Socioculturelle", "Salle Socioculturelle"

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        APPROVED = "approved", "Acceptee"
        REJECTED = "rejected", "Rejetee"

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="event_requests")
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_requests")
    title = models.CharField(max_length=150)
    description = models.TextField()
    event_date = models.DateField()
    event_time = models.TimeField(null=True, blank=True, verbose_name="Heure")
    location = models.CharField(
        max_length=50,
        choices=Location.choices,
        default=Location.SALLE_12,
        verbose_name="Lieu",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande evenement: {self.title}"


class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_registrations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.username} inscrit {self.event.title}"
