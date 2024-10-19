from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Device

@receiver(user_logged_in)
def log_device(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')

    # Check if this device is already registered for the user
    device, created = Device.objects.get_or_create(
        user=user,
        ip_address=ip,
        user_agent=user_agent
    )

    if created:
        print(f"New device registered: {ip} - {user_agent}")
    else:
        print(f"Existing device logged in: {ip} - {user_agent}")

def get_client_ip(request):
    """Utility function to get the client's IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
