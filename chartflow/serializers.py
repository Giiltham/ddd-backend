from rest_framework import serializers
from .models import User, Artist, Country, Chart, ChartEntry, CountryCluster

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['iso2', 'internet_users', 'population']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role']

class ArtistSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    name = serializers.CharField()
    nationality = serializers.CharField()
    manager = UserSerializer(allow_null=True)

    class Meta:
        model = Artist
        fields = ['id', 'user', 'name', 'manager', 'nationality']

class ChartEntrySerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    rank = serializers.CharField()

    class Meta:
        model = ChartEntry
        fields = ['id', 'artist', 'rank']

class ChartSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    entries = ChartEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Chart
        fields = ['id', 'country', 'entries']

class CountryClusterSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = CountryCluster
        fields = ['country', 'cluster']