from . import models
from rest_framework import serializers
from USErs.models import Customer
from restaurant.models import Table, Restaurant

from datetime import datetime, timedelta
from django.utils import timezone


class CustomerMiniSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Customer
        fields = ('username',)


class TableMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('restoran', 'number', 'status')



class RestoranMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('name',)




class ReservationCreateSerializer(serializers.ModelSerializer):
    reservation_date = serializers.DateField(
        format="%d-%m-%Y",
        input_formats=['%d-%m-%Y', '%d.%m.%Y']
    )
    reservation_time = serializers.TimeField(
        format='%H:%M',
        input_formats=['%H:%M', '%H-%M']
    )
    created_at = serializers.DateTimeField(
        format='%d-%m-%Y %H:%M',
        read_only=True
    )
    client = CustomerMiniSerializer(read_only=True)

    class Meta:
        model = models.Reservation
        fields = (
            'restoran', 
            'table', 
            'client', 
            'guests_count',
            'status',
            'created_at', 
            'reservation_date', 
            'reservation_time', 
            'duration_hours'
        )
        read_only_fields = ('restoran', 'client', 'created_at', 'status')

    def validate(self, attrs):
        table = attrs.get('table')
        res_date = attrs.get('reservation_date')
        res_time = attrs.get('reservation_time')
        duration = attrs.get('duration_hours', 1.0)


        now = timezone.now()
        reservation_datetime = datetime.combine(res_date, res_time)

        if timezone.is_aware(timezone.now()):
            reservation_datetime = timezone.make_aware(reservation_datetime)

        if reservation_datetime < now:
            raise serializers.ValidationError(
                {"reservation_time": "Ótip ketken waqıtqa bron jaratıwǵa bolmaydı!"})


        view = self.context.get('view')
        restoran_id = None
        if view and hasattr(view, 'kwargs'):
            restoran_id = view.kwargs.get('restaurant_pk') or view.kwargs.get('pk') or view.kwargs.get('restaurant_id')

        # 2. Tanlangan stol usi restoranga tiyisli ekenligini tekseriw
        if table and restoran_id:
            if str(table.restoran_id) != str(restoran_id):
                raise serializers.ValidationError({
                    "table": "Bul stol bul restoranga tiyisli emes!"
                })

        # 3. Waqit ham sane boyinsha  conflict tekseriw
        if table and res_date and res_time:
            # Bronning baslaniw ham tamamlaniw waqti
            start_datetime = datetime.combine(res_date, res_time)
            end_datetime = start_datetime + timedelta(hours=float(duration))

            # Usi stol ushin sol kunge belgilangen aktiv bronlardi bazadan aliw
            existing_reservations = models.Reservation.objects.filter(
                table=table,
                reservation_date=res_date,
                status__in=['jaratildi', 'tastiqlandi']
            )

            # eger UPDATE boip atirgan bolsa
            if self.instance:
                existing_reservations = existing_reservations.exclude(pk=self.instance.pk)

            for res in existing_reservations:
                existing_start = datetime.combine(res.reservation_date, res.reservation_time)
                existing_end = existing_start + timedelta(hours=float(res.duration_hours))

                # Waqit araligi ustpe-ust  tusiwin tekseriw
                if start_datetime < existing_end and end_datetime > existing_start:
                    raise serializers.ValidationError({
                        "reservation_time": "Usi waqit araliginda stol alleqashan bron qilingan!"
                    })

        return attrs


class ReservationListSerializer(serializers.ModelSerializer):
    reservation_date = serializers.DateField(
        format="%d-%m-%Y",
        input_formats=['%d-%m-%Y', '%d.%m.%Y']
    )

    reservation_time = serializers.TimeField(
        format='%H:%M',
        input_formats=['%H:%M', '%H-%M']

    )
    
    client = CustomerMiniSerializer(source='user.username', read_only=True)
    table = TableMiniSerializer(read_only=True)
    restoran = RestoranMiniSerializer(read_only=True)
    class Meta:
        model = models.Reservation
        fields = (
            'restoran',
            'table',
            'client',
            'reservation_date',
            'reservation_time',
            'duration_hours',
            'status'
        )



class ReservationMeSerializer(serializers.ModelSerializer):
    restoran  = RestoranMiniSerializer(read_only=True)
    table = TableMiniSerializer(read_only=True)
    
    reservation_date = serializers.DateField(
        format="%d-%m-%Y",
        input_formats=['%d-%m-%Y', '%d.%m.%Y']
    )

    reservation_time = serializers.TimeField(
        format='%H:%M',
        input_formats=['%H:%M', '%H-%M']

    )

    class Meta:
        model = models.Reservation
        fields = ('restoran', 'table', 'reservation_date', 'status', 'reservation_time', 'duration_hours')



class ReservationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservation
        fields = ('id', 'status')

    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)

        # Eger status 'jawildi' ga o'zgerse bronga jalgangan stol statusin ozgertemiz
        if new_status == 'jawildi' and instance.table:
            table = instance.table
            table.status = 'bos'
            table.save()

        instance.status = new_status
        instance.save()
        return instance


class ReservatioCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservation
        fields = ('id', 'status')
        read_only_fields = ('id', 'status')