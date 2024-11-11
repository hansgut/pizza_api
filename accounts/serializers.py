from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'date_of_birth']


class UserSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        """
        Check if the email is unique.
        """
        user = self.context.get("request").user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    # # validate that profile is passed
    # def validate_profile(self, data):
    #     if not data.get('profile'):
    #         raise serializers.ValidationError("Profile is required")
    #     return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        CustomerProfile.objects.filter(user=user).update(**profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()

        profile.phone_number = profile_data.get('phone_number', profile.phone_number)
        profile.date_of_birth = profile_data.get('date_of_birth', profile.date_of_birth)
        profile.save()

        return instance
