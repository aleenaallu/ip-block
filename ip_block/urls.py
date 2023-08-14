from django.urls import path
from ip_block.ipblock_middleware import IPBlockMiddleware
from ip_block.views import IPBlockView,IPUnblockView,BlockedIPListView ,FailedLoginAttemptListView , PermanentIPBlockView

urlpatterns = [
    path('block/',IPBlockView.as_view(),name='ip block'),
    path('unblock/',IPUnblockView.as_view(),name='ip unblock'),
    path('blocked-ips/', BlockedIPListView.as_view(), name='blocked-ips-list'),
    path('failed-login-attempts/',FailedLoginAttemptListView.as_view(),name='failed-login-attempt'),
    path('permanent-block-ip/', PermanentIPBlockView.as_view(), name='permanent-block-ip')
]