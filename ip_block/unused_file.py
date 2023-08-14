# from django.db import models
# from datetime import timedelta
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated
# from django.core.cache import cache
# from rest_framework.views import APIView
# from .models import BlockedIP, PermanentBlockedIP, BlockedIO, FailedLoginAttempt
# from rest_framework.generics import ListAPIView
# from rest_framework.permissions import IsAdminUser
# from .serializers import BlockedIPSerializer


# class IPBlockMiddleware:
#     blocked_request_tracker = {}

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         ip_address = request.META.get('REMOTE_ADDR')

#         if self.is_ip_permently_blocked(ip_address):
#             return Response('Access Forbidden', status=403)

#         if self.is_ip_blocked(ip_address):
#             return Response('Access Forbidden', status=403)

#         if request.path == '/block-ip/':
#             block_ip_view = IPBlockView.as_view()
#             return block_ip_view(request)
#         elif request.path == '/unblock-ip/':
#             unblock_ip_view = IPUnblockView.as_view()
#             return unblock_ip_view(request)
#         elif request.path == '/blocked-ips/':
#             blocked_ip_list_view = BlockedIPListView.as_view()
#             return blocked_ip_list_view(request)

#         response = self.get_response(request)

#         if response.status_code == 401:
#             self.handle_failed_login(ip_address, request.user)

#         return response

#     def is_ip_blocked(self, ip_address):
#         return BlockedIP.objects.filter(ip_address=ip_address).exists()

#     def is_ip_permently_blocked(self, ip_address):
#         return PermanentBlockedIP.objects.filter(ip_address=ip_address, is_permanently_blocked=True).exists()

#     def block_ip(self, ip_address, io_type='manual', duration_minutes=10):
#         blocked_ip, created = BlockedIP.objects.get_or_create(ip_address=ip_address)
#         blocked_ip.failed_login_attempts = 0
#         blocked_ip.save()
#         BlockedIO.objects.create(ip=blocked_ip, io_type=io_type, duration_minutes=duration_minutes)

#     def unblock_ip(self, ip_address):
#         print(f"Unblocking IP: {ip_address}")
#         blocked_ip = BlockedIP.objects.filter(ip_address=ip_address)
#         if blocked_ip:
#             blocked_ip.delete()

#     def get_blocked_ips(self):
#         blocked_ips = BlockedIP.objects.values_list('ip_address', flat=True)
#         return list(blocked_ips)

#     def block_ip_manually(self, ip_addresses):
#         for ip_address in ip_addresses:
#             if ip_address in self.blocked_request_tracker and self.blocked_request_tracker[ip_address]:
#                 # IP address is already blocked, skip the block request
#                 continue
#             self.block_ip(ip_address, io_type='manual')
#             self.blocked_request_tracker[ip_address] = True

#     def handle_failed_login(self, ip_address, user):
#         cache_key = f"login_attempts_{ip_address}"
#         login_attempts = cache.get(cache_key, default=0) + 1

#         if login_attempts == 5:
#             failed_login = FailedLoginAttempt.objects.create(ip_address=ip_address)
#             failed_login.save()

#             self.block_ip(ip_address, io_type="login_attempt", duration_minutes=10)
#             blocked_message = "Access blocked due to multiple failed login attempts"
#             return Response(blocked_message, status=403)

#         failed_login = FailedLoginAttempt.objects.filter(ip_address=ip_address).first()
#         if failed_login:
#             failed_login.count += 1
#         else:
#             failed_login = FailedLoginAttempt(ip_address=ip_address, count=1)
#         failed_login.save()

#         cache.set(cache_key, login_attempts, timeout=timedelta(minutes=10))
#         if login_attempts >= 3:
#             captcha_url = "https://api-ai-sv-module.hilalcart.com/captcha/"
#         else:
#             captcha_url = None

#         warning_message = f"Warning: Too many failed login attempts. {5 - login_attempts} attempts remaining."
#         return Response(warning_message, status=403)


# class PermanentIPBlockMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         ip_address = request.META.get('REMOTE_ADDR')

#         if self.is_ip_permanently_blocked(ip_address):
#             return Response('Access Forbidden', status=403)

#         response = self.get_response(request)
#         return response

#     def is_ip_permanently_blocked(self, ip_address):
#         return PermanentBlockedIP.objects.filter(ip_address=ip_address, is_permanently_blocked=True).exists()


# class IPBlockView(APIView):
#     blocked_request_tracker = {}

#     def post(self, request):
#         ip_addresses = request.data.get('ip_address', [])
#         if not ip_addresses:  # No IP addresses provided
#             return Response('No IP addresses provided', status=400)

#         ip_block_middleware = IPBlockMiddleware(get_response=None)

#         for ip_address in ip_addresses:
#             if ip_address in ip_block_middleware.blocked_request_tracker and ip_block_middleware.blocked_request_tracker[ip_address]:
#                 # IP address is already blocked, skip the block request
#                 continue

#         ip_block_middleware.block_ip_manually(ip_addresses)
#         ip_block_middleware.blocked_request_tracker[ip_address] = True

#         return Response('IP addresses blocked successfully', status=200)


# class IPUnblockView(APIView):
#     unblocked_request_tracker = {}

#     def post(self, request):
#         ip_addresses = request.data.get('ip_addresses', [])
#         if not ip_addresses:  # No IP addresses provided
#             return Response('No IP addresses provided', status=400)

#         ip_block_middleware = IPBlockMiddleware(get_response=None)
#         for ip_address in ip_addresses:
#             if ip_block_middleware.is_ip_blocked(ip_address):
#                 if ip_address in self.unblocked_request_tracker and self.unblocked_request_tracker[ip_address]:
#                     return Response('IP is already being unblocked', status=200)

#                 ip_block_middleware.unblock_ip(ip_address)
#                 ip_block_middleware.blocked_request_tracker.pop(ip_address, None)
#                 self.unblocked_request_tracker[ip_address] = True

#         return Response('IP addresses unblocked successfully', status=200)


# class BlockedIPListView(ListAPIView):
#     queryset = BlockedIP.objects.all()
#     serializer_class = BlockedIPSerializer


# class FailedLoginAttemptListView(APIView):
#     def get(self, request):
#         failed_attempts = FailedLoginAttempt.objects.all()
#         response_data = []

#         for attempt in failed_attempts:
#             attempt_data = {
#                 'ip_address': attempt.ip_address,
#                 'count': FailedLoginAttempt.objects.filter(ip_address=attempt.ip_address).count()
#             }
#             response_data.append(attempt_data)

#         return Response(response_data)

#     def post(self, request):
#         ip_address = request.data.get('ip_address')

#         if not ip_address:
#             return Response('Failed login attempt recorded', status=400)

#         failed_login_attempt = FailedLoginAttempt(ip_address=ip_address)
#         failed_login_attempt.save()

#         return Response('Failed login attempt recorded', status=200)


# class PermanentIPBlockView(APIView):
#     permission_classes = [IsAdminUser]

#     def post(self, request):
#         ip_address = request.data.get('ip_address')

#         if not ip_address:
#             return Response('No IP address provided', status=400)

#         PermanentBlockedIP.objects.create(ip_address=ip_address, is_permanently_blocked=True)

#         return Response('IP address permanently blocked', status=200)
