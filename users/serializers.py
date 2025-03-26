from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password 
from rest_framework.validators import UniqueValidator
from tasks.models import Task



class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles validation and user creation with password hashing.
    """
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with that email already exists.")]
    )
    
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with that username already exists.")]
    )
   
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'} 
    )
  
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm password",
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        
        fields = ('id', 'username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, attrs):
        """
        Check that the two password entries match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.
        Handles password hashing.
        """
    
        validated_data.pop('password2')
        password = validated_data.pop('password')

        user = User.objects.create_user(**validated_data)
        # user.set_password(password) # create_user does this already
        # user.save()

        return user