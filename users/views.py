from rest_framework import generics, permissions 
from .serializers import RegisterSerializer 
from django.contrib.auth.models import User

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for non-superuser registration.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
