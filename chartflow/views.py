from collections import defaultdict
from django.forms import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from chartflow.permissions import ArtistViewPermissions, ChartEntryViewPermissions, ChartViewPermissions, CountryClusterViewPermissions, CountryViewPermissions, UserViewPermissions
from .models import User, Artist, Country, Chart, ChartEntry, CountryCluster
from .serializers import (
    AdminArtistSerializer, UserSerializer, ArtistSerializer, CountrySerializer, 
    ChartSerializer, ChartEntrySerializer, CountryClusterSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminUser|UserViewPermissions)

    @action(detail=False, methods=['post'], permission_classes=())
    def logout(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=())
    def authenticate(self, request):
        try:
            user = User.objects.filter(email=request.data.get('email')).first()
            if user and user.check_password(request.data.get('password')):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            else:
                raise ValidationError("Invalid credentials")
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            user = UserSerializer(request.user)
            return Response(user.data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = (IsAuthenticated, IsAdminUser|ArtistViewPermissions)
    
    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        if request.user.role in ["manager"]:
            queryset = queryset.filter(manager=request.user)
            
        if request.user.role in ["admin"]:
            self.serializer_class = AdminArtistSerializer

        serializer = self.get_serializer(queryset.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def nationalities(self,request):
        return Response(Artist.objects.all().values_list("nationality", flat=True).distinct())
        
    @action(detail=False, methods=["get"])
    def me(self,request):
        try:
            artist = ArtistSerializer(request.user.artist_profile)
            return Response(artist.data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': "No artist profile found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk):
        try:
            pass
            artist = Artist.objects.get(id=pk)
            chart_entries = ChartEntry.objects.filter(artist=artist)
            return Response(ChartEntrySerializer(chart_entries, many=True).data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAuthenticated, IsAdminUser|CountryViewPermissions)


class ChartViewSet(viewsets.ModelViewSet):
    queryset = Chart.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']
    serializer_class = ChartSerializer
    permission_classes = (IsAuthenticated, IsAdminUser|ChartViewPermissions)

    @action(detail=False, methods=['get'], url_path='countries')
    def countries(self, request, country_iso2=None):
        try:
            countries = Chart.objects.values('country').distinct()
            countries = [country["country"] for country in countries]
            return Response({'countries': countries}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


class ChartEntryViewSet(viewsets.ModelViewSet):
    queryset = ChartEntry.objects.all()
    serializer_class = ChartEntrySerializer
    permission_classes = (IsAuthenticated, IsAdminUser|ChartEntryViewPermissions)


class CountryClusterViewSet(viewsets.ModelViewSet):
    queryset = CountryCluster.objects.all()
    serializer_class = CountryClusterSerializer
    permission_classes = (IsAuthenticated, IsAdminUser|CountryClusterViewPermissions)


class ExportAnalysisViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='potential/(?P<artist_id>\d+)')
    def export_potential(self, request, artist_id=None):
        try:
            artist = Artist.objects.get(id=artist_id)
            nationality = artist.nationality
            foreign_charts_not_present_in = Chart.objects.exclude(country=nationality).exclude(entries__artist=artist)
            same_nationality_artists = Artist.objects.filter(nationality=nationality).exclude(id=artist_id)
            foreign_entries = ChartEntry.objects.filter(
                chart__in=foreign_charts_not_present_in,
                artist__in=same_nationality_artists
            )

            grouped = defaultdict(lambda: defaultdict(lambda: {"name": "", "rank": 200}))
            for entry in foreign_entries:
                country = entry.chart.country.iso2
                name = entry.artist.name
                rank = entry.rank
                artist_info = grouped[country][name]
                artist_info.update({"name": name, "rank": min(artist_info["rank"], rank)})

            result = [{"country": country, "artists": list(artists.values())} for country, artists in grouped.items()]
            
            return Response(result)
        except Artist.DoesNotExist:
            return Response({'error': ValidationError("Artist not found")}, status=status.HTTP_400_BAD_REQUEST)