from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator

class Country(models.Model):
    iso2 = models.CharField(max_length=2, unique=True, primary_key=True)
    internet_users = models.FloatField()
    population = models.IntegerField()

    def __str__(self):
        return self.iso2

class User(AbstractUser):
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('artist', 'Artist')
    ], default='artist')

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='chartflow_user_groups',  # Unique related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='chartflow_user_permissions',  # Unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Artist(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='artist_profile', null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='managed_artists', limit_choices_to={'role': 'manager'})
    nationality = models.CharField(max_length=2)

    def __str__(self):
        return self.name

class Chart(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='charts')
    
    class Meta:
        unique_together = ['country']

    def __str__(self):
        return f"Chart for {self.country.iso2}"

class ChartEntry(models.Model):
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE, related_name='entries')
    artist = models.ForeignKey(Artist, to_field="id",on_delete=models.CASCADE, related_name='chart_entries')
    rank = models.IntegerField()

    class Meta:
        unique_together = ['chart', 'artist']

    def __str__(self):
        return f"{self.artist.name} at rank {self.rank} in {self.chart.country.iso2}"

class CountryCluster(models.Model):
    class ClusterChoices(models.TextChoices):
        MATURE = 'MATURE', 'Mature'
        POTENTIAL = 'POTENTIAL', 'Potential'

    country = models.OneToOneField(Country, on_delete=models.CASCADE, related_name='cluster')
    cluster = models.CharField(max_length=20, choices=ClusterChoices.choices)

    def __str__(self):
        return f"{self.country.iso2} - {self.cluster}"
