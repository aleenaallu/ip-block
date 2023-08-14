from functools import wraps
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.cache import cache
from datetime import timedelta
from ip_block.models import *


def ip_block_decorators(get_response):
    @wraps(get_response)
    def ip_decorator(request):
        ip_address = request.META.get('REMOTE_ADDR')

        if is_ip_permanently_blocked(ip_address):
            return Response('Access Forbidden', status=403)

        if is_ip_blocked(ip_address):
            return Response('Access Forbidden', status=403)

        response = get_response(request)

        if response.status_code == 401:
            handle_failed_login(ip_address, request.user)

        return response

    def is_ip_blocked(ip_address):
        return BlockedIP.objects.filter(ip_address=ip_address).exists()

    def is_ip_permanently_blocked(ip_address):
        return PermanentBlockedIP.objects.filter(ip_address=ip_address, is_permanently_blocked=True).exists()
    
    def block_ip(self, ip_address, io_type='manual', duration_minutes=10):
        blocked_ip, created = BlockedIP.objects.get_or_create(ip_address=ip_address)
        blocked_ip.failed_login_attempts = 0
        blocked_ip.save()
        BlockedIO.objects.create(ip=blocked_ip, io_type=io_type, duration_minutes=duration_minutes)


    def handle_failed_login(ip_address, user):
        cache_key = f"login_attempts_{ip_address}"
        login_attempts = cache.get(cache_key, default=0) + 1

        if login_attempts == 5:
            failed_login = FailedLoginAttempt.objects.create(ip_address=ip_address)
            failed_login.save()

            block_ip(ip_address, io_type="login_attempt", duration_minutes=10)
            blocked_message = "Access blocked due to multiple failed login attempts"
            return Response(blocked_message, status=403)

        failed_login = FailedLoginAttempt.objects.filter(ip_address=ip_address).first()
        if failed_login:
            failed_login.count += 1
        else:
            failed_login = FailedLoginAttempt(ip_address=ip_address, count=1)
        failed_login.save()

        cache.set(cache_key, login_attempts, timeout=timedelta(minutes=10))

        warning_message = f"Warning: Too many failed login attempts. {5 - login_attempts} attempts remaining."
        return Response(warning_message, status=403)

    return ip_decorator


def permanent_ip_block_decorators(get_response):
    @wraps(get_response)
    def ip_decorator(request):
        ip_address = request.META.get('REMOTE_ADDR')

        if is_ip_permanently_blocked(ip_address):
            return Response('Access Forbidden', status=403)

        response = get_response(request)
        return response

    def is_ip_permanently_blocked(ip_address):
        return PermanentBlockedIP.objects.filter(ip_address=ip_address, is_permanently_blocked=True).exists()

    return ip_decorator
