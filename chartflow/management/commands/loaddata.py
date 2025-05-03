from django.core.management.base import BaseCommand, CommandError
import pandas as pd

from chartflow.models import Artist, Chart, ChartEntry, Country, CountryCluster

class Command(BaseCommand):
    help = "Closes the specified poll for voting"
    datasets_root = "datasets/"

    def load_dataset(self, dataset) -> pd.DataFrame | None:
        try:
            df = pd.read_csv(f"{self.datasets_root}{dataset}")
            df.reset_index()
            return df
        except:
            return None

    def load_countries(self, countries_df: pd.DataFrame) -> list[Country]:
        countries = []
        for _, country_df in countries_df.iterrows():
            country = Country(
                iso2=country_df["country_iso2"], 
                internet_users=country_df["%_internet"], 
                population=country_df["population_total"]
            )
            country.save()
            countries.append(country)
        return countries

    def load_artists(self, artists_df: pd.DataFrame) -> list[Artist]:
        artists = []
        for _, artist_df in artists_df.iterrows():
            artist = Artist(
                name=artist_df["artistName"], 
                nationality=artist_df["artistCountry"] 
            )
            artist.save()
            artists.append(artist)
        return artists
    
    def load_charts(self, charts_df: pd.DataFrame, countries_df: pd.DataFrame) -> list[Chart]:
        charts = []
        for _, country_df in countries_df.iterrows():
            chart = Chart(
                country = Country.objects.get(iso2=country_df["country_iso2"])
            )
            chart.save()
            for _, chart_df in charts_df[charts_df["country_iso2"] == country_df["country_iso2"]].iterrows():
                print(f"{chart_df["artistName"]} - {chart_df["artistCountry"]}")
                chart_entry = ChartEntry(
                    chart=chart,
                    artist = Artist.objects.get(name=chart_df["artistName"], nationality=chart_df["artistCountry"]),
                    rank=int(chart_df["currentRank"])
                )
                chart_entry.save()
            charts.append(chart)
        return charts
    
    def load_clusters(self, clusters_df: pd.DataFrame) -> list[CountryCluster]:
        clusters = []
        for _, cluster_df in clusters_df.iterrows():
            cluster = int(cluster_df["cluster"])
            if cluster == 0:
                cluster_choice = CountryCluster.ClusterChoices.POTENTIAL
            elif cluster == 1:
                cluster_choice = CountryCluster.ClusterChoices.MATURE
            elif cluster == 2:
                # USA, we consider it as MATURE instead of being alone in it's cluster
                cluster_choice = CountryCluster.ClusterChoices.MATURE
            elif cluster == 3:
                # India, we consider it as POTENTIAL because of huge local scene
                cluster_choice = CountryCluster.ClusterChoices.POTENTIAL
            else:
                raise CommandError(f"Cluster id not known : {cluster}")

            cluster = CountryCluster(
                country=Country.objects.get(pk=cluster_df["country_iso2"]),
                cluster=cluster_choice
            )
            cluster.save()
            clusters.append(cluster)
        return clusters
    
    def handle(self, *args, **options):
        CountryCluster.objects.all().delete()
        ChartEntry.objects.all().delete()
        Chart.objects.all().delete()
        Artist.objects.all().delete()
        Country.objects.all().delete()

        if (countries_df := self.load_dataset("countries.csv")) is not None:
            self.load_countries(countries_df)
        else:
            raise CommandError("Couldn't load dataset countries")
        
        if (artists_df := self.load_dataset("artists.csv")) is not None:
            self.load_artists(artists_df)
        else:
            raise CommandError("Couldn't load dataset artists")
        
        if (charts_df := self.load_dataset("charts.csv")) is not None:
            self.load_charts(charts_df, countries_df)
        else:
            raise CommandError("Couldn't load dataset charts")
        
        if (clusters_df := self.load_dataset("clusters.csv")) is not None:
            self.load_clusters(clusters_df)
        else:
            raise CommandError("Couldn't load dataset clusters")
