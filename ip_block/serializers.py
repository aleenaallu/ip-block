from rest_framework import serializers
from ip_block.models import * 

class BlockedIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedIP
        # fields = ['ip_address']
        fields = '__all__'

class FailedLoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedLoginAttempt
        # fields = ['id', 'ip_address', 'timestamp']
        fields ='__all__'
