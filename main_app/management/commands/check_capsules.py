from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from main_app.models import TimeCapsule

class Command(BaseCommand):
    help = 'Check for time capsules that are ready to be opened and send email notifications'
    
    def handle(self, *args, **options):
        """Handle the command execution"""
        # Find capsules that are ready to be opened but haven't been opened yet
        now = timezone.now()
        ready_capsules = TimeCapsule.objects.filter(open_date__lte=now, is_opened=False)
        
        self.stdout.write(f"Found {ready_capsules.count()} capsules ready to be opened")
        
        # Send email notifications
        for capsule in ready_capsules:
            user = capsule.user
            if user.email:
                # Construct the message
                subject = f"Your Time Capsule '{capsule.title}' is Ready to Open!"
                message = (
                    f"Hello {user.username},\n\n"
                    f"Great news! Your time capsule '{capsule.title}' that you created on "
                    f"{capsule.created_at.strftime('%B %d, %Y')} is now ready to be opened.\n\n"
                    f"Visit the site to unlock your memories: {settings.BASE_URL}{reverse('capsule-detail', kwargs={'pk': capsule.pk})}\n\n"
                    f"We hope you enjoy rediscovering these moments from your past!\n\n"
                    f"Regards,\nThe DearMe Team"
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]
                
                try:
                    send_mail(subject, message, from_email, recipient_list)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Sent email notification to {user.username} ({user.email}) for capsule '{capsule.title}'"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to send email to {user.username} ({user.email}): {str(e)}"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"User {user.username} has no email address, skipping notification for capsule '{capsule.title}'"
                    )
                )
