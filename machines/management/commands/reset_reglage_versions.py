from django.core.management.base import BaseCommand
from machines.models import ReglageEKO, ReglageEKOHistory, ReglageEKOChange

class Command(BaseCommand):
    help = "Reset versions and history of all ReglageEKO"

    def handle(self, *args, **options):
        ReglageEKOHistory.objects.all().delete()
        ReglageEKOChange.objects.all().delete()
        ReglageEKO.objects.update(version=1)

        self.stdout.write(self.style.SUCCESS(
            "✅ Versions, snapshots et changelog réinitialisés"
        ))