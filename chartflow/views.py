from django.forms import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import User, Artist, Country, Chart, ChartEntry, CountryCluster
from .serializers import (
    UserSerializer, ArtistSerializer, CountrySerializer, 
    ChartSerializer, ChartEntrySerializer, CountryClusterSerializer
)
from .services import (
    UserManagementService, RoleManagementService, AuthenticationService,
    ChartRetrievalService, ExportAnalysisService
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django_filters.rest_framework import DjangoFilterBackend

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = UserManagementService.create_user(
                email=request.data.get('email'),
                password=request.data.get('password'),
                username=request.data.get('username'),
                role=request.data.get('role'),
                artist_id=request.data.get('artist_id'),
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            user = UserManagementService.update_user(
                user_id=self.get_object().id,
                email=request.data.get('email'),
                username=request.data.get('username'),
                role=request.data.get('role'),
                nationality_iso2=request.data.get('nationality_iso2'),
                manager_id=request.data.get('manager_id')
            )
            return Response(UserSerializer(user).data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
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

    @action(detail=False, methods=['post'])
    def authenticate(self, request):
        try:
            data = AuthenticationService.authenticate(
                email=request.data.get('email'),
                password=request.data.get('password')
            )
            return Response(data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            user = UserSerializer(request.user)
            return Response(user.data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        try:
            user = RoleManagementService.assign_role(
                user_id=pk,
                role=request.data.get('role')
            )
            return Response(UserSerializer(user).data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

    @action(detail=False, methods=["get"])
    def me(self,request):
        try:
            artist = ArtistSerializer(request.user.artist_profile)
            return Response(artist.data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': "No artist profile found"}, status=status.HTTP_404_NOT_FOUND)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class ChartViewSet(viewsets.ModelViewSet):
    queryset = Chart.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']
    serializer_class = ChartSerializer

    @action(detail=False, methods=['get'], url_path='country/(?P<country_iso2>[^/.]+)')
    def by_country(self, request, country_iso2=None):
        try:
            charts = ChartRetrievalService.get_charts_by_country(country_iso2)
            return Response(ChartSerializer(charts, many=True).data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='countries')
    def countries(self, request, country_iso2=None):
        try:
            countries = ChartRetrievalService.get_charts_countries()
            countries = [country["country"] for country in countries]
            return Response({'countries': countries}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

class ChartEntryViewSet(viewsets.ModelViewSet):
    queryset = ChartEntry.objects.all()
    serializer_class = ChartEntrySerializer

    @action(detail=False, methods=['get'], url_path='manager/(?P<manager_id>\d+)')
    def for_manager(self, request, manager_id=None):
        try:
            entries = ChartRetrievalService.get_charts_for_manager(manager_id)
            return Response(ChartEntrySerializer(entries, many=True).data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='artist/(?P<artist_id>\d+)')
    def for_artist(self, request, artist_id=None):
        try:
            entries = ChartRetrievalService.get_charts_for_artist(artist_id)
            return Response(ChartEntrySerializer(entries, many=True).data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_entry(self, request):
        try:
            entry = ChartRetrievalService.update_chart_entry(
                chart_id=request.data.get('chart_id'),
                artist_id=request.data.get('artist_id'),
                rank=request.data.get('rank')
            )
            return Response(ChartEntrySerializer(entry).data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

class CountryClusterViewSet(viewsets.ModelViewSet):
    queryset = CountryCluster.objects.all()
    serializer_class = CountryClusterSerializer

    @action(detail=False, methods=['get'], url_path='development/(?P<country_iso2>[^/.]+)')
    def country_development(self, request, country_iso2=None):
        try:
            data = ExportAnalysisService.get_country_development(country_iso2)
            return Response(data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

class ExportAnalysisViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='potential/(?P<artist_id>\d+)')
    def export_potential(self, request, artist_id=None):
        try:
            data = ExportAnalysisService.estimate_export_potential(artist_id)
            return Response(data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)