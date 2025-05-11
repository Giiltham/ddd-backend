
from django.core.management import BaseCommand

from chartflow.models import Artist, User
import random

class Command(BaseCommand):
    help = "Create users"

    def handle(self, *args, **options):
        User.objects.all().delete()
        
        admin = User(
            username="admin",
            email="admin@gmail.com",
            role="admin"
        )
        admin.set_password("password")
        admin.is_staff = True
        admin.save()
        
        # Managers
        for i in range(50):
            manager = User(
                username=f"manager{i+1}",
                email=f"manager{i+1}@gmail.com",
                role="manager"
            )
            manager.set_password("password")
            manager.save()
            
            # Artists
            artists = Artist.objects.filter(manager__isnull=True).order_by('?').all()[:random.randint(0, 10)]
            for x, artist in enumerate(artists):
                artist_user = User(
                    username=f"artist.{i+1}.{x+1}",
                    email=f"artist.{i+1}.{x+1}@gmail.com",
                    role="artist"
                )
                artist_user.set_password("password")
                artist_user.save() 
                
                artist.manager = manager
                artist.user = artist_user
                artist.save()