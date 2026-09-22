from rest_framework.serializers import (
    ModelSerializer, CharField, ReadOnlyField, 
    ValidationError, Serializer
)
from django.contrib.auth.models import User
from .models import Customer, Xizmetker, RestoranAdminmodel
from django.db import transaction

class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name', 'password']




class CustomerViewSerializer(ModelSerializer):
    username = CharField(write_only=True)
    first_name = CharField(write_only=True, required=False, allow_blank=True)
    last_name = CharField(write_only=True, required=False, allow_blank=True)

    user_username = ReadOnlyField(source='user.username')
    user_first_name = ReadOnlyField(source='user.first_name')
    user_last_name = ReadOnlyField(source='user.last_name')

    class Meta:
        model = Customer
        fields = ('id', 'username', 'first_name', 'last_name', 'role', 'user_username', 'user_first_name', 'user_last_name')
        read_only_fields = ('role',)


class CustomerSerializer(ModelSerializer):
    username = CharField(write_only=True)
    first_name = CharField(write_only=True, required=False, allow_blank=True)
    last_name = CharField(write_only=True, required=False, allow_blank=True)
    password = CharField(write_only=True)

    user_username = ReadOnlyField(source='user.username')
    user_first_name = ReadOnlyField(source='user.first_name')
    user_last_name = ReadOnlyField(source='user.last_name')

    class Meta:
        model = Customer
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'role', 'user_username', 'user_first_name', 'user_last_name')
        read_only_fields = ('role',)


    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')


        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            customer = Customer.objects.create(user=user, role='klient')

        return customer


    def validate_username(self, value):
        user = self.instance.user if self.instance else None
        if User.objects.filter(username=value).exclude(pk=user.pk if user else None).exists():
            raise ValidationError("Bul username bant!")
        return value


    def update(self, instance, validated_data):
        username = validated_data.pop('username', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)

        user = instance.user

        with transaction.atomic():
            if username is not None:
                user.username = username
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            user.save()

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance



class ChangePasswordSerializer(Serializer):
    old_password = CharField(write_only=True)
    new_password = CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Eski parol qate!")
        return value


        return value



    

class XizmetkerSerializer(ModelSerializer):
    username = CharField(write_only=True)
    first_name = CharField(write_only=True, required=True, allow_blank=False)
    last_name = CharField(write_only=True, required=True, allow_blank=False)
    password = CharField(write_only=True)

    user_username = ReadOnlyField(source='user.username')
    user_first_name = ReadOnlyField(source='user.first_name')
    user_last_name = ReadOnlyField(source='user.last_name')

    
    
    class Meta:
        model = Xizmetker
        fields = ('id', 'restoran', 'username', 'is_active','first_name', 'last_name', 'password', 'role', 'user_username', 'user_first_name', 'user_last_name')
        read_only_fields = ('restoran',)
    
    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
                
            xizmetker = Xizmetker.objects.create(user=user, **validated_data)

        return xizmetker  

    def update(self, instance, validated_data):
        # 1. User maydonlarini ajratib olamiz (PATCH'da kelmagan bo'lishi ham mumkin)
        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)
        first_name = validated_data.pop("first_name", None)
        last_name = validated_data.pop("last_name", None)

        with transaction.atomic():
            # 2. User modelini yangilaymiz
            user = instance.user
            if username is not None:
                user.username = username
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if password:
                user.set_password(password)  # Parolni xeshlab saqlash shart!

            user.save()

            # 3. Xizmetker modelining o'zini yangilaymiz (masalan: role)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance                  





class RestoranAdminSerializer(ModelSerializer):

    username = CharField(write_only=True)
    first_name = CharField(write_only=True, required=True, allow_blank=False)
    last_name = CharField(write_only=True, required=True, allow_blank=False)
    password = CharField(write_only=True)

    user_username = ReadOnlyField(source='user.username')
    user_first_name = ReadOnlyField(source='user.first_name')
    user_last_name = ReadOnlyField(source='user.last_name')

    class Meta:
        model = RestoranAdminmodel
        fields = ('id', 'restoran', 'username', 'is_active', 'first_name', 'last_name', 'password', 'role', 'user_username', 'user_first_name', 'user_last_name')
        
        read_only_fields = ('role',)
    
    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
                
            admin = RestoranAdminmodel.objects.create(user=user, role='restoran admin', **validated_data)
        return admin