from . import models
from .serializer import (
    CustomerSerializer, XizmetkerSerializer, 
    RestoranAdminSerializer, ChangePasswordSerializer,
    CustomerViewSerializer
)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema




from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .permissions import IsCustomerOwner, IsRestoranAdmin, XizmetkerDetailPermission

from restaurant.permissions import warnings

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


class CustomerListView(viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated, IsCustomerOwner]
    serializer_class = CustomerSerializer

    def get_serializer_class(self):
        if self.action == 'change_password':
            return ChangePasswordSerializer
        return self.serializer_class


    @extend_schema(methods=['GET'], responses={200: CustomerSerializer})
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        customer = getattr(request.user, 'customers', None)

        if not customer:
            Response({"detail": "Profil tabilmadi!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(customer)

        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(methods=['PUT', 'PATCH'], request=CustomerViewSerializer, responses={200:CustomerViewSerializer})
    @action(detail=False, methods=['put', 'patch'], url_path='me/update')
    def update_profile(self, request):
        customer = getattr(request.user, 'customers', None)

        if not customer:
            return Response(
                {"detail": "Profil tabilmadi!"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(
            customer, 
            data=request.data, 
            partial=(request.method == "PATCH")
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(methods=['POST'], request=ChangePasswordSerializer, responses={200: {"detail": "Parol ozgertirildi!"}})
    @action(detail=False, methods=['post'], url_path='me/change-password')
    def change_password(self, request):
        """Faqat o'z parolini o'zgartirish"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {"detail": "Parol muvaffaqiyatli o'zgartirildi."}, 
            status=status.HTTP_200_OK
        )



    
class XizmetkerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Xizmetker.objects.all()
    serializer_class = XizmetkerSerializer
    permission_classes = [XizmetkerDetailPermission]

    def get_queryset(self):
        user = self.request.user

        if (user and user.is_authenticated and 
        hasattr(user, 'adminler') 
        and hasattr(user.adminler, 'restoran')):
            
            if not user.adminler.is_active:
                self.message = warnings[0]
                return False
            return models.Xizmetker.objects.filter(restoran=user.adminler.restoran)

        return models.Xizmetker.objects.none()


class RestoranAdminViewSet(viewsets.ModelViewSet):
    queryset = models.RestoranAdminmodel.objects.all()
    serializer_class = RestoranAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]