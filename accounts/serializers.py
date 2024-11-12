from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomerProfile, Address


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'date_of_birth']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'zip_code', 'is_default', 'address_type']

    def create(self, validated_data):
        user = self.context.get("request").user
        address = Address.objects.create(customer=user, **validated_data)
        return address

    def update(self, instance, validated_data):
        instance.street = validated_data.get('street', instance.street)
        instance.city = validated_data.get('city', instance.city)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.is_default = validated_data.get('is_default', instance.is_default)
        instance.address_type = validated_data.get('address_type', instance.address_type)
        instance.save()
        if instance.is_default:
            Address.objects.filter(customer=instance.customer).exclude(pk=instance.pk).update(is_default=False)
        return instance


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
