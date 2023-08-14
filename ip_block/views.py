from django.shortcuts import render
# Create your views here.
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from ip_block.ipblock_middleware import IPBlockMiddleware , PermanentIPBlockMiddleware
from rest_framework.permissions import IsAuthenticated
from ip_block.serializers import BlockedIPSerializer
from .models import *
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser


class IPBlockView(APIView):
    blocked_request_tracker = {}

    def post(self, request):
        """
        API endpoint to manually block IP addresses.
        Requires IP addresses to be provided in the request body as a list.
        """

        ip_addresses = request.data.get('ip_address', [])
        # print(ip_addresses)
        

        if not ip_addresses:  # No IP addresses provided
            return Response('No IP addresses provided', status=400)

        ip_block_middleware = IPBlockMiddleware(get_response=None)

        for ip_address in ip_addresses:
            if ip_address in ip_block_middleware.blocked_request_tracker and ip_block_middleware.blocked_request_tracker[ip_address]:
                # IP address is already blocked, skip the block request
                continue

        ip_block_middleware.block_ip_manually(ip_addresses)
        ip_block_middleware.blocked_request_tracker[ip_address] = True

        return Response('IP addresses blocked successfully', status=200)

    
class IPUnblockView(APIView):
    #permission_classes = [IsAuthenticated]
    unblocked_request_tracker ={}

    def post(self, request):
        """
        API endpoint to manually unblock IP addresses.
        Requires IP addresses to be provided in the request body as a list.
        """
        ip_address = request.data.get('ip_addresses', [])
        print("xxxx",ip_address)

        if not ip_address:  # No IP addresses provided
            return Response('No IP addresses provided', status=400)

        ip_block_middleware = IPBlockMiddleware(get_response=None)

        for ip_addresses in ip_address:
            # Check if the IP is currently blocked
            if ip_block_middleware.is_ip_blocked(ip_addresses):
                # Check if the IP is already being unblocked
                if ip_addresses in self.unblocked_request_tracker and self.unblocked_request_tracker[ip_address]:
                    return Response('IP is already being unblocked',status=200)  
                
                ip_block_middleware.unblock_ip(ip_addresses)   # Unblock the IP
                # Remove the IP from the blocked_request_tracker to indicate it's unblocked
                ip_block_middleware.blocked_request_tracker.pop(ip_addresses,None)
                # Add the IP to the unblocked_request_tracker to track that it's being unblocked
                self.unblocked_request_tracker[ip_addresses] = True
            
        return Response('IP addresses unblocked successfully', status=200)
        # else:
        #     return Response('IP is not blocked',status=200)

class BlockedIPListView(ListAPIView):
    #API endpoint to list all blocked IP addresses. 
    queryset = BlockedIP.objects.all()
    serializer_class = BlockedIPSerializer


class FailedLoginAttemptListView(APIView):
    def get(self, request):
        # API endpoint to retrieve the count of failed login attempts for each IP address.

        failed_attempts = (
            FailedLoginAttempt.objects.values('ip_address')
            .annotate(count=Count('ip_address'))
            .values('ip_address', 'count')
        )

        return Response(failed_attempts)
 
    
    def post(self,request):
        """
        API endpoint to record a failed login attempt for an IP address.
        Requires the IP address to be provided in the request body.
        """
        ip_address = request.data.get('ip_address')

        if not ip_address:
            return Response('Failed login attempt  recorded' ,status=400)
        
        failed_login_attempt = FailedLoginAttempt(ip_address=ip_address)
        failed_login_attempt.save()
        
        return Response('Failed login attempt recorded',status=200)
    

#++++++++++++++++++++++++ PERMANENT IP BLOCK MIDDLEWARE ++++++++++++++++++++++++++++++++

# permanent IP block view is accessible only by admins
class PermanentIPBlockView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self,request):
        """
        API endpoint to permanently block an IP address.
        Requires the IP address to be provided in the request body.
        """
        ip_address = request.data.get('ip_address')

        if not ip_address:
            return Response('No IP address provided',status=400)
        
        PermanentBlockedIP.objects.create(ip_address=ip_address,is_permanently_blocked =True)

        return Response('IP address permanently blocked',status=200)
    


    