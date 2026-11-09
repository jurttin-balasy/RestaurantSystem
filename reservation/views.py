from django.db import transaction
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

    
    @extend_schema(methods=['GET'], responses={200:serializers.ReservationMeSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def my(self, request):
        user = request.user
        customer = getattr(user, 'customers', None)
        if not customer:
            return Response([], status=status.HTTP_200_OK)
        
        reservations = models.Reservation.objects.filter(client=customer).select_related('restaurant', 'table')
        serializer = serializers.ReservationMeSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(methods=['PATCH'], request=None, responses={200: serializers.ReservationMeSerializer})
    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        user = request.user
        customer = getattr(user, 'customers', None)
        
        # Faqat usi klientke tiyisli ham aktiv brondi alamiz
        reservation = models.Reservation.objects.filter(id=pk, client=customer).first()
        
        if not reservation:
            return Response(
                {"detail": "Bron tabilmadi yaki sizge tiyisli emes."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if reservation.status == 'completed':
            return Response(
                {"detail": "Jawilgan brondi biykar qilip bolmaydi."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if reservation.status == 'cancelled':
            return Response(
                {"detail": "Bul bron alleqashan biykar etilgen."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            reservation.status = 'cancelled'
            reservation.save(update_fields=['status'])

            if reservation.table:

                reservation.table.status = 'free'
                reservation.table.save(update_fields=['status'])

            

        serializer = self.get_serializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)






# api/reservations/
class AdminReservationViewSet(mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    queryset = models.Reservation.objects.all()
    serializer_class = serializers.ReservationListSerializer
    permission_classes = [AdminReservation]
    http_method_names = ['get', 'patch']

    
    def get_queryset(self):
        user = self.request.user
        admin = getattr(user, 'adminler', None)
        waiter = getattr(user, 'xizmetkerler', None)
        if admin and getattr(admin, 'restaurant', None):
            return models.Reservation.objects.filter(restaurant=admin.restaurant).select_related('table', 'client')
        if waiter and getattr(waiter, 'restaurant', None):
            return models.Reservation.objects.filter(restaurant=waiter.restaurant).select_related('table', 'client')
        return models.Reservation.objects.none()


    
    @extend_schema(
        methods=["PATCH"], 
        request=serializers.ReservationStatusUpdateSerializer, 
        responses={200: serializers.ReservationListSerializer}  
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def status(self, request, pk=None):
        reservation = self.get_object()
        serializer = serializers.ReservationStatusUpdateSerializer(reservation, data=request.data, partial=True)

        if serializer.is_valid():
            updated_reservation = serializer.save()

            table = updated_reservation.table
            new_status = updated_reservation.status

            if new_status == 'confirmed':
                table.status = 'occupied'
                table.save()
                
            elif new_status in ['completed', 'cancelled']:
                table.status = 'free'
                table.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)