from typing import Any
from django.db import models
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from ip_block.models import *
from django.core.cache import cache
from rest_framework.permissions import IsAdminUser


# +++++++++++++++++++ COMMON IP BLOCKING MIDDLEWARE +++++++++++++++++++++++++++++++
class IPBlockMiddleware:
    permission_classes = [IsAuthenticated]
    blocked_request_tracker = {}  # Dictionary to track IP block requests
    
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("IP block")
        # Retrieve the IP address from the request's META data
        ip_address = request.META.get('REMOTE_ADDR') 
        
        # Check if the IP address is permanently blocked
        if self.is_ip_permently_blocked(ip_address):
            return Response('Access Forbidden', status=403)
        
        # Check if the IP address is temporarily blocked
        if self.is_ip_blocked(ip_address):
            return Response('Access Forbidden', status=403)
        
        # Pass the request to the next middleware or view function in the chain
        response = self.get_response(request)
        
        # Handle failed login attempts
        if response.status_code == 401:
            self.handle_failed_login(ip_address,request.user)
        return response
    
    def is_ip_blocked(self,ip_address):
        # Check if the IP address is blocked in the BlockedIP model
        return BlockedIP.objects.filter(ip_address=ip_address).exists()
    
    def is_ip_permently_blocked(self,ip_address):
        # Check if the IP address is permanently blocked in the PermanentBlockedIP model
        return PermanentBlockedIP.objects.filter(ip_address=ip_address,is_permanently_blocked=True).exists()
    
    def block_ip(self,ip_address,io_type='manual',duration_minutes=10):
        # Block the IP address by creating a BlockedIP object and associating a BlockedIO object
        blocked_ip ,created = BlockedIP.objects.get_or_create(ip_address=ip_address)
        blocked_ip.failed_login_attempts = 0
        blocked_ip.save()
        BlockedIO.objects.create(ip=blocked_ip,io_type=io_type,duration_minutes=duration_minutes)

    def unblock_ip(self,ip_address):
        # Unblock the IP address by deleting the BlockedIP object
        print(f"Unblocking IP: {ip_address}")
        blocked_ip = BlockedIP.objects.filter(ip_address=ip_address)
        if blocked_ip:
            blocked_ip.delete()

    def get_blocked_ips(self):
        # Retrieve a list of blocked IP addresses from the BlockedIP model
        blocked_ips =BlockedIP.objects.values_list('ip_address',flat=True)
        return list(blocked_ips)
    
    def block_ip_manually(self,ip_addresses):
        # Manually block a list of IP addresses
        print(ip_addresses,"manual func")
        for ip_address in ip_addresses:
            if ip_address in self.blocked_request_tracker and self.blocked_request_tracker[ip_address]:
                # IP address is already blocked, skip the block request
                continue
            self.block_ip(ip_address,io_type='manual')
            self.blocked_request_tracker[ip_address] = True

    # ===================== failed login case ================

    def handle_failed_login(self,ip_address,user):
        # Create a cache key using the IP address to store the login attempts count in the cache
        cache_key = f"login_attempts_{ip_address}"
        # Retrieve the current login attempts count from the cache. If the cache key doesn't exist, default to 0.
        login_attempts = cache.get(cache_key,default=0)+1
        
        # If there have been 5 consecutive failed login attempts from the same IP address
        if login_attempts == 5: 
        # Store the IP address in the FailedLoginAttempt table
            failed_login = FailedLoginAttempt.objects.create(ip_address=ip_address)
            failed_login.save()

            # Block the IP address temporarily for failed login attempts
            self.block_ip(ip_address,io_type="login_attempt",duration_minutes=10)
            blocked_message = "Access blocked due to multiple failed login attempts"
            return Response(blocked_message,status=403)
        
        # Update the count in FailedLoginAttempt model
        failed_login = FailedLoginAttempt.objects.filter(ip_address=ip_address).first()
        if failed_login:
            failed_login.count += 1
        else:
            failed_login = FailedLoginAttempt(ip_address=ip_address, count=1)
        failed_login.save()
        
        # Update the cache with the new login attempts count and set a timeout of 10 minutes for the cache entry
        cache.set(cache_key,login_attempts,timeout=timedelta(minutes=10))
        
        # If there have been 3 or more failed login attempts, show a CAPTCHA to prevent automated login attempts
        if login_attempts >= 3:
            captcha_url = "https://api-ai-xx-module.xxx.com/captcha/"
        else:
        # If less than 3 failed login attempts, do not show a CAPTCHA
            captcha_url = None
        
        # Construct a warning message indicating the number of remaining attempts (up to 5 attempts) for the user to log in successfully
        warning_message = f"Warning: Too many failed login attempts.{5 - login_attempts} attempts remaining."
        # Return a 403 HTTP status code with the warning message
        return Response(warning_message,status=403)

#++++++++++++++++++ PERMANENTLY IP BLOCKING MIDDLEWARE+++++++++++++++++

class PermanentIPBlockMiddleware:
    print("adminside ipblock")
    permission_classes = [IsAdminUser]
    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self,request):
        # Retrieve the IP address from the request's META data
        ip_address = request.META.get('REMOTE_ADDR')

        # Check if the IP address is permanently blocked
        if self.is_ip_permanently_blocked(ip_address):
            return Response('Access Forbidden' ,status=403)
        
        # Pass the request to the next middleware or view function in the chain
        response=self.get_response(request)
        return response
    
    def is_ip_permanently_blocked(self,ip_address):
        # Check if the IP address is permanently blocked in the PermanentBlockedIP model
        return PermanentBlockedIP.objects.filter(ip_address=ip_address, is_permanently_blocked = True).exists()
     