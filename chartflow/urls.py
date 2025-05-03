from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ArtistViewSet, CountryViewSet, ChartViewSet,
    ChartEntryViewSet, CountryClusterViewSet, ExportAnalysisViewSet
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'artists', ArtistViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'charts', ChartViewSet)
router.register(r'chart-entries', ChartEntryViewSet)
router.register(r'country-clusters', CountryClusterViewSet)
router.register(r'export-analysis', ExportAnalysisViewSet, basename='export-analysis')
urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]