from rest_framework.serializers import (
    ModelSerializer, CharField, ReadOnlyField, 
    ValidationError, SerializerMethodField
)

from rest_framework.validators import UniqueValidator
from .models import Customer, Xizmetker, RestoranAdminmodel, CustomUser
from django.db import transaction
from restaurant.models import Restaurant


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id','phone_number', 'first_name', 'last_name', 'password']



from rest_framework import serializers
from django.contrib.auth import get_user_model
from restaurant.models import Restaurant 

User = get_user_model()


class RestaurantMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name')



class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    restaurant = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 
            'phone_number', 
            'first_name', 
            'last_name', 
            'email', 
            'role', 
            'restaurant'
        )
        read_only_fields = ('role', 'restaurant')


    def get_role(self, obj):
        # obj -> CustomUser obyekti
        if hasattr(obj, 'adminler'):
            return obj.adminler.role
        elif hasattr(obj, 'xizmetkerler'):
            return obj.xizmetkerler.role
        elif hasattr(obj, 'customers'):
            return obj.customers.role
        elif obj.is_superuser:
            return "superadmin"
        return None


    def get_restaurant(self, obj):
        rest = None
        if hasattr(obj, 'adminler') and getattr(obj.adminler, 'restaurant', None):
            rest = obj.adminler.restaurant
        elif hasattr(obj, 'xizmetkerler') and getattr(obj.xizmetkerler, 'restaurant', None):
            rest = obj.xizmetkerler.restaurant
        elif hasattr(obj, 'customers') and getattr(obj.customers, 'restaurant', None):
            rest = obj.customers.restaurant
        
       
        if rest:
            return RestaurantMiniSerializer(rest).data
      
        return None


# get user/me customer
class CustomerViewSerializer(ModelSerializer):

    restaurant = ReadOnlyField(source='restaurant.name')
    
    phone_number = CharField(source='user.phone_number', write_only=True)
    first_name = CharField(source='user.first_name', write_only=True, required=False, allow_blank=True)
    last_name = CharField(source='user.last_name', write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Customer
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'email', 'role', 'restaurant')
        read_only_fields = ('role',)



# create / sign_up_Serializer
class CustomerSerializer(ModelSerializer):
    phone_number = CharField(source='user.phone_number')
    first_name = CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = CharField(source='user.last_name', required=False, allow_blank=True)
    password = CharField(write_only=True)
    restaurant = SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'password', 'role', 'restaurant')
        read_only_fields = ('role','restaurant')


    def validate_phone_number(self, value):
        user = self.instance.user if (self.instance and hasattr(self.instance, 'user')) else None
        user_pk = user.pk if user else None

        if CustomUser.objects.filter(phone_number=value).exclude(pk=user_pk).exists():
            raise ValidationError("Bul telefon nomer tizimnen otken !")
        return value


    def create(self, validated_data): 
        user_data = validated_data.pop('user')

        phone_number = user_data.get('phone_number')
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        password = validated_data.pop('password')


        with transaction.atomic():
            user = CustomUser.objects.create_user(
                phone_number=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            customer = Customer.objects.create(user=user, role='customer', **validated_data)

        return customer



    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')

        phone_number = user_data.get('phone_number', None)
        first_name = user_data.get('first_name', None)
        last_name = user_data.get('last_name', None)

        user = instance.user

        with transaction.atomic():
            if phone_number is not None:
                user.phone_number = phone_number
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            user.save()

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance

    def get_restaurant(self, obj):
        return None



    
# get, list 
class XizmetkerSerializer(ModelSerializer):
    # phone_number = CharField(write_only=True)
    # first_name = CharField(write_only=True, required=True, allow_blank=False)
    # last_name = CharField(write_only=True, required=True, allow_blank=False)

    phone_number = CharField(source='user.phone_number')
    first_name = CharField(source='user.first_name')
    last_name = CharField(source='user.last_name')
    password = CharField(write_only=True)

    
    # restaurant_name = CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Xizmetker
        fields = ('id', 'restaurant', 'phone_number', 'is_active','first_name', 'last_name', 'password', 'role')
        read_only_fields = ('restaurant',)

    
    def create(self, validated_data):
        user_data = validated_data.pop('user')

        phone_number = user_data.get('phone_number')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        password = validated_data.pop('password')

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                phone_number=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
                
            xizmetker = Xizmetker.objects.create(user=user, **validated_data)

        return xizmetker  

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        phone_number = user_data.get("phone_number", None)
        first_name = user_data.get("first_name", None)
        last_name = user_data.get("last_name", None)
        password = validated_data.pop("password", None)

        with transaction.atomic():
            # 2. User modelin janalaymiz
            user = instance.user
            if phone_number is not None:
                user.phone_number = phone_number
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if password:
                user.set_password(password)  # Paroldi xeshlap saqlaw!

            user.save()

            # 3. Xizmetker modelinin ozin janalaymiz
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance                  





class RestoranAdminSerializer(ModelSerializer):

    # phone_number = CharField(write_only=True, validators=[
    #         UniqueValidator(
    #             queryset=CustomUser.objects.all(),
    #             message="Bul telefon nomer alleqashan dizimnen otken!"
    #         )
    #     ])
    
    # first_name = CharField(write_only=True, required=True, allow_blank=False)
    # last_name = CharField(write_only=True, required=True, allow_blank=False)
    # password = CharField(write_only=True)

    phone_number = CharField(source='user.phone_number')
    first_name = CharField(source='user.first_name')
    last_name = CharField(source='user.last_name')
    password = CharField(write_only=True)

    restaurant_name = ReadOnlyField(source='restaurant.name')

    class Meta:
        model = RestoranAdminmodel
        fields = ('id', 'restaurant', 'restaurant_name', 'phone_number', 'first_name', 'last_name', 'password')
        
        read_only_fields = ('role',)



    def create(self, validated_data):
        user_data = validated_data.pop('user')

        phone_number = user_data.get('phone_number')
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        password = validated_data.pop('password')

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                phone_number=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
                
            admin = RestoranAdminmodel.objects.create(user=user, role='restaurant_admin', **validated_data)
        return admin


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user    
            for attr, value in  user_data.items():
                setattr(user, attr, value)

            user.save()

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()
            return instance
        
class RestoranInfoSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name')

class XizmetkerViewSerializer(ModelSerializer):
    restaurant = RestoranInfoSerializer(read_only=True)
    phone_number = ReadOnlyField(source='user.phone_number')
    first_name = ReadOnlyField(source='user.first_name')
    last_name = ReadOnlyField(source='user.last_name')
    

    class Meta:
        model = Xizmetker
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'role', 'restaurant')




class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = SerializerMethodField()

    def validate_phone_number(self, value):
        # Raqamni shu yerning o'zidayoq tekshiramiz
        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Bunday telefon raqamli foydalanuvchi tizimda topilmadi.")
        return value


    def get_role(self):
        if hasattr(User, 'adminler'):
            return User.adminler.role
        elif hasattr(User, 'xizmetkerler'):
            return User.xizmetkerler.role
        elif hasattr(User, 'customers'):
            return User.customers.role
        elif User.is_superuser:
            return "superadmin"
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError({ "old_password": ["Eski parol noto'g'ri."] })
        return value
