from django.db.models import query
from rest_framework import serializers
from rest_framework.fields import IntegerField
from .models import User, Artist, Country, Chart, ChartEntry, CountryCluster

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['iso2', 'internet_users', 'population']

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        depth = 1  
        fields = ['id', 'user', 'name', 'manager', 'nationality']

class UserSerializer(serializers.ModelSerializer):
    artist_id = IntegerField(write_only=True, required=False)
    artist_profile = ArtistSerializer(read_only=True)   
    class Meta:
        model = User
        depth = 1
        fields = ['id', 'email', 'username', 'password', 'role', 'artist_profile', 'artist_id']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }
        
    def validate(self, attrs):
        role = attrs.get("role")
        artist_id = attrs.get("artist_id")

        if role == "artist" and not artist_id:
            raise serializers.ValidationError({
                "artist_id": "This field is required when role is 'artist'."
            })

        if role == "artist" and artist_id:
            try:
                Artist.objects.get(pk=artist_id)
            except:
                raise serializers.ValidationError({
                    "artist_id": "This artist does not exist."
                })
            if Artist.objects.filter(user__isnull=False, pk=artist_id).exists():
                raise serializers.ValidationError({
                    "artist_id": "This artist profile is already associated with another user."
            })

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        artist_id = validated_data.pop('artist_id', None)
        role = validated_data.get('role')

        # Create the User instance
        user = User(**validated_data)
        user.set_password(password)
        user.full_clean()
        
        if role == "admin":
            user.is_staff = True
            
        user.save()

        # If the role is 'artist', associate the artist_profile with the user
        if role == "artist" and artist_id:
            artist = Artist.objects.get(pk=artist_id)
            artist.user = user  # Associate the artist profile with the user
            artist.save()

        return user


class ChartEntrySerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()

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