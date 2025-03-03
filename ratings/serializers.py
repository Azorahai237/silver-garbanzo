from rest_framework import serializers
from .models import Professor, Module, ModuleInstance, Rating

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'

class ModuleInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleInstance
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'