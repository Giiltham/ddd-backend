from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from chartflow.serializers import ArtistSerializer, CountrySerializer, UserSerializer
from .models import User, Artist, Chart, ChartEntry, Country, CountryCluster

class UserManagementService:
    @staticmethod
    def create_user(email, password, username, role, artist_id):
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            role=role
        )
        
        if role == 'artist':
            #if not nationality_iso2 or not Country.objects.filter(iso2=nationality_iso2).exists():
            if artist_id and (artist := Artist.objects.get(pk=artist_id)):
                artist.user = user
                artist.save()
            else:
                user.delete()
                raise ValidationError("Invalid nationality")

        return user

    @staticmethod
    def update_user(user_id, email=None, username=None, role=None, nationality_iso2=None, manager_id=None):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError("User not found")
        
        if email and User.objects.exclude(id=user_id).filter(email=email).exists():
            raise ValidationError("Email already exists")
        
        if email:
            user.email = email
        if username:
            user.username = username
        if role:
            user.role = role
        user.save()

        if user.role == 'artist' and (nationality_iso2 or manager_id):
            try:
                artist = user.artist_profile
            except Artist.DoesNotExist:
                raise ValidationError("Artist profile not found")
            
            if nationality_iso2:
                try:
                    artist.nationality = Country.objects.get(iso2=nationality_iso2)
                except Country.DoesNotExist:
                    raise ValidationError("Invalid nationality")
            
            if manager_id:
                try:
                    artist.manager = User.objects.get(id=manager_id, role='manager')
                except User.DoesNotExist:
                    raise ValidationError("Invalid manager")
            
            artist.save()
        
        return user

    @staticmethod
    def delete_user(user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
        except User.DoesNotExist:
            raise ValidationError("User not found")

class RoleManagementService:
    @staticmethod
    def assign_role(user_id, role):
        try:
            user = User.objects.get(id=user_id)
            user.role = role
            user.save()
            if role == 'artist' and not hasattr(user, 'artist_profile'):
                Artist.objects.create(
                    user=user,
                    nationality=Country.objects.first()  # Default to first country
                )
            return user
        except User.DoesNotExist:
            raise ValidationError("User not found")

class AuthenticationService:
    @staticmethod
    def authenticate(email, password):
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }
        raise ValidationError("Invalid credentials")

class ChartRetrievalService:
    @staticmethod
    def get_charts_countries():
        return Chart.objects.values('country').distinct()
    
    @staticmethod
    def get_charts_by_country(country_iso2):
        try:
            country = Country.objects.get(iso2=country_iso2)
            charts = Chart.objects.filter(country=country)
            return charts
        except Country.DoesNotExist:
            raise ValidationError("Country not found")

    @staticmethod
    def get_charts_for_manager(manager_id):
        try:
            manager = User.objects.get(id=manager_id, role='manager')
            artists = Artist.objects.filter(manager=manager)
            return ChartEntry.objects.filter(artist__in=artists)
        except User.DoesNotExist:
            raise ValidationError("Manager not found")

    @staticmethod
    def get_charts_for_artist(artist_id):
        try:
            artist = Artist.objects.get(user__id=artist_id)
            return ChartEntry.objects.filter(artist=artist)
        except Artist.DoesNotExist:
            raise ValidationError("Artist not found")

    @staticmethod
    def update_chart_entry(chart_id, artist_id, rank):
        try:
            chart = Chart.objects.get(id=chart_id)
            artist = Artist.objects.get(user__id=artist_id)
            entry, created = ChartEntry.objects.update_or_create(
                chart=chart,
                artist=artist,
                defaults={'rank': rank}
            )
            return entry
        except (Chart.DoesNotExist, Artist.DoesNotExist):
            raise ValidationError("Invalid chart or artist")

class ExportAnalysisService:
    @staticmethod
    def get_country_development(country_iso2):
        try:
            country = Country.objects.get(iso2=country_iso2)
            cluster = CountryCluster.objects.get(country=country)
            charts = Chart.objects.filter(country=country)
            artists = Artist.objects.filter(chart_entries__chart__in=charts).distinct()
            return {
                'country': CountrySerializer(country).data,
                'cluster': cluster.cluster,
                'artist_count': artists.count(),
                'chart_count': charts.count()
            }
        except (Country.DoesNotExist, CountryCluster.DoesNotExist):
            raise ValidationError("Country or cluster not found")

    @staticmethod
    def estimate_export_potential(artist_id):
        try:
            artist = Artist.objects.get(user__id=artist_id)
            nationality = artist.nationality
            foreign_charts = Chart.objects.exclude(country=nationality)
            same_nationality_artists = Artist.objects.filter(nationality=nationality).exclude(user__id=artist_id)
            foreign_entries = ChartEntry.objects.filter(
                chart__in=foreign_charts,
                artist__in=same_nationality_artists
            )
            return {
                'artist': ArtistSerializer(artist).data,
                'foreign_chart_entries': foreign_entries.count(),
                'potential_countries': list(set([entry.chart.country.iso2 for entry in foreign_entries]))
            }
        except Artist.DoesNotExist:
            raise ValidationError("Artist not found")
