from . import models
from .serializer import (
    CustomerSerializer, XizmetkerSerializer,
    RestoranAdminSerializer, UserProfileSerializer,
    ResetPasswordSerializer, ChangePasswordSerializer
)



from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
User = get_user_model()


from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .permissions import XizmetkerDetailPermission


class CustomerSignUpView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerSerializer

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Siz dizimnen ottiniz!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# users/me


class UserView(viewsets.GenericViewSet):
    serializer_class = UserProfileSerializer 


    def get_permissions(self):

        if self.action == 'reset_password':
            return [IsAdminUser()]
        
        return [IsAuthenticated()]


    def get_serializer_class(self):
        if self.action == 'reset_password':
            return ResetPasswordSerializer
        if self.action == 'change_password':
            return ChangePasswordSerializer
        
        return UserProfileSerializer


    
    @extend_schema(methods=['GET'], responses={200: UserProfileSerializer})
    @extend_schema(methods=['PATCH'], request=UserProfileSerializer, responses={200:UserProfileSerializer})
    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user  # Kim so'rov yuborgan bo'lsa, o'sha CustomUser

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            # Ism, familiya yoki emailni yangilash uchun
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @extend_schema(methods=['POST'], request=ChangePasswordSerializer, responses={200: dict})
    @action(detail=False, methods=['POST'], url_path='me/change-password')
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()

            return Response({'detail': "Parol o'zgertirildi."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       




    @extend_schema(methods=['POST'], request=ResetPasswordSerializer, responses={200: dict})
    @action(detail=False, methods=['post'], url_path='reset_password')
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            new_password = serializer.validated_data['new_password']

            # Biz aniq bilamizki user bor (Serializer buni tasdiqlab bo'ldi)
            user = User.objects.get(phone_number=phone_number)
            if hasattr(user, 'adminler'):
                role = user.adminler.role
            if hasattr(user, 'xizmetkerler'):
                role = user.xizmetkerler.role
            if hasattr(user, 'customers'):
                role = user.customers.role
            
            if user.is_superuser:
                role = 'superadmin'

            user.set_password(new_password)
            user.save()
            
            return Response({"detail": "Parol tiklendi!", 'role': role}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



        


        
        

        


    
class XizmetkerDetailView(mixins.RetrieveModelMixin, 
                        mixins.UpdateModelMixin, 
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    
    queryset = models.Xizmetker.objects.all()
    serializer_class = XizmetkerSerializer
    permission_classes = [XizmetkerDetailPermission]




   
# Restaurant Adminler
class RestoranAdminViewSet(viewsets.ModelViewSet):
    queryset = models.RestoranAdminmodel.objects.all()
    serializer_class = RestoranAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


