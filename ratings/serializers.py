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
    def validate(self, data):
        module_instance = data.get('module_instance')
        professor = data.get('professor')

        # Check if the professor is associated with the module instance
        if not module_instance.professors.filter(id=professor.id).exists():
            raise serializers.ValidationError("Professor is not teaching this module instance")
        
        return data