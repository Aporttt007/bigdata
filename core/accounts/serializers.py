from rest_framework import serializers
from .models import CustomUser, Area, Region

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'area']

class AreaSerializer(serializers.ModelSerializer):
    regions = RegionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Area
        fields = ['id', 'name', 'code', 'regions']

class UserSerializer(serializers.ModelSerializer):
    area = AreaSerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    manager = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role', 'phone', 'iin', 'area', 'region', 'ticket', 'link', 'manager']
        read_only_fields = ['ticket']

class UserRegistrationSerializer(serializers.ModelSerializer):
    area_id = serializers.IntegerField(write_only=True)
    region_id = serializers.IntegerField(write_only=True)
    manager_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'role', 'phone', 'iin', 'area_id', 'region_id', 'manager_id', 'link']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        area = Area.objects.filter(id=data['area_id']).first()
        if not area:
            raise serializers.ValidationError({"area_id": "Invalid area ID"})
        
        region = Region.objects.filter(id=data['region_id'], area=area).first()
        if not region:
            raise serializers.ValidationError({"region_id": "Invalid region ID or region does not belong to the specified area"})
        
        if 'manager_id' in data and data['manager_id']:
            manager = CustomUser.objects.filter(id=data['manager_id'], role='manager').first()
            if not manager:
                raise serializers.ValidationError({"manager_id": "Invalid manager ID or user is not a manager"})
        
        return data

    def create(self, validated_data):
        area_id = validated_data.pop('area_id')
        region_id = validated_data.pop('region_id')
        manager_id = validated_data.pop('manager_id', None)
        password = validated_data.pop('password')
        
        user = CustomUser(
            **validated_data,
            area_id=area_id,
            region_id=region_id,
            manager_id=manager_id
        )
        user.set_password(password)
        user.save()
        return user

class TicketSerializer(serializers.ModelSerializer):
    area = AreaSerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'ticket', 'area', 'region']
