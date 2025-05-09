from django.forms import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from chartflow.permissions import ArtistViewPermissions, ChartEntryViewPermissions, ChartViewPermissions, CountryClusterViewPermissions, CountryViewPermissions, UserViewPermissions
from .models import User, Artist, Country, Chart, ChartEntry, CountryCluster
from .serializers import (
    UserSerializer, ArtistSerializer, CountrySerializer, 
    ChartSerializer, ChartEntrySerializer, CountryClusterSerializer
)
from .services import (
    AuthenticationService,
    ChartRetrievalService, ExportAnalysisService
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminUser|UserViewPermissions)


    # def update(self, request, *args, **kwargs):
    #     try:
    #         user = UserManagementService.update_user(
    #             user_id=self.get_object().id,
    #             email=request.data.get('email'),
    #             username=request.data.get('username'),
    #             role=request.data.get('role'),
    #             nationality_iso2=request.data.get('nationality_iso2'),
    #             manager_id=request.data.get('manager_id')
    #         )
    #         return Response(UserSerializer(user).data)
    #     except ValidationError as e:
    #         return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

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


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = (IsAuthenticated, IsAdminUser|ArtistViewPermissions)
    
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
    permission_classes = (IsAuthenticated, IsAdminUser|ChartEntryViewPermissions)



class CountryClusterViewSet(viewsets.ModelViewSet):
    queryset = CountryCluster.objects.all()
    serializer_class = CountryClusterSerializer
    permission_classes = (IsAuthenticated, IsAdminUser|CountryClusterViewPermissions)

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