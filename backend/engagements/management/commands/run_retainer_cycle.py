from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from engagements.services import run_retainer_cycle


class Command(BaseCommand):
    help = "Generate retainer billing drafts for a given YYYY-MM period."

    def add_arguments(self, parser):
        parser.add_argument("period", type=str, help="Target billing period in YYYY-MM format")
        parser.add_argument("--user", type=str, dest="username", help="Username executing the cycle (for audit)")

    def handle(self, *args, **options):
        period = options["period"]
        username = options.get("username")
        if not username:
            raise CommandError("--user is required to attribute audit trail")
        try:
            actor = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"User '{username}' not found") from exc
        summary = run_retainer_cycle(period=period, actor=actor)
        self.stdout.write(self.style.SUCCESS(f"Retainer cycle completed: {summary}"))
