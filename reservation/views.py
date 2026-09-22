from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from . import models
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from USErs.permissions import IsCustomerOwner

from .permissions import AdminReservation
from . import serializers

# api/my_reservations/
class ReservationMe(viewsets.GenericViewSet):
    serializer_class = serializers.ReservationMeSerializer
    permission_classes = [IsCustomerOwner]

    
    @extend_schema(methods=['GET'], responses={200:serializers.ReservationMeSerializer})
    @action(detail=False, methods=['get'])
    def _ (self, request):
        user = request.user
        customer = getattr(user, 'customers', None)
        if not customer:
            return Response([], status=status.HTTP_200_OK)
        
        reservations = models.Reservation.objects.filter(client=customer).select_related('restoran', 'table')
        serializer = serializers.ReservationMeSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(methods=['PATCH'], request=None, responses={200: serializers.ReservationMeSerializer})
    @action(detail=True, methods=['patch'], url_path='cancel_reservation')
    def cancel_reservation(self, request, pk=None):
        user = request.user
        customer = getattr(user, 'customers', None)
        
        # Faqat usi klientke tiyisli ham aktiv brondi alamiz
        reservation = models.Reservation.objects.filter(id=pk, client=customer).first()
        
        if not reservation:
            return Response(
                {"detail": "Bron tabilmadi yaki sizge tiyisli emes."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if reservation.status == 'jawildi':
            return Response(
                {"detail": "Jawilgan brondi biyjar qilip bolmaydi."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = 'bikor_etildi'
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AdminReservationViewSet(mixins.ListModelMixin, 
                              viewsets.GenericViewSet):
    queryset = models.Reservation.objects.all()
    serializer_class = serializers.ReservationListSerializer
    permission_classes = [AdminReservation]



    def get_queryset(self):
        user = self.request.user
        admin = getattr(user, 'adminler', None)
        if admin and getattr(admin, 'restoran', None):
            return models.Reservation.objects.filter(restoran=admin.restoran).select_related('table', 'client')
        return models.Reservation.objects.none()

    @extend_schema(
        methods=["PATCH"], 
        request=serializers.ReservationStatusUpdateSerializer, 
        responses={200: serializers.ReservationStatusUpdateSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='change_status')
    def change_status(self, request, pk=None):
        reservation = self.get_object()
        serializer = serializers.ReservationStatusUpdateSerializer(reservation, data=request.data, partial=True)

        if serializer.is_valid():
            updated_reservation = serializer.save()

            table = updated_reservation.table
            new_status = updated_reservation.status

            if new_status == 'tastiqlandi':
                table.status = 'bant'
                table.save()
                
            elif new_status in ['jawildi', 'biykar_etildi']:
                table.status = 'bos'
                table.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)