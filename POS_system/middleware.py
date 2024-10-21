from django.shortcuts import redirect
from django.contrib.auth import logout
from .models import Device
from django.utils import timezone

class DeviceAuthenticationMiddleware:
    """Ensure the device is registered for the current user."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow unauthenticated users to access login page
        if request.user.is_authenticated:
            ip = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')

            # Check if the current device is registered
            device_exists = Device.objects.filter(
                user=request.user, ip_address=ip, user_agent=user_agent
            ).exists()

            if not device_exists:
                # Log out the user and redirect to login if device is not registered
                logout(request)
                return redirect('login')  # Change 'login' to your login URL or view name

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
