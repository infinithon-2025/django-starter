from rest_framework import serializers
from .models import Project, ProjectMaterial, AIRequest, Summary, Item, Recommendation


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProjectMaterialSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = ProjectMaterial
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AIRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRequest
        fields = '__all__'
        read_only_fields = ('created_at',)


class SummarySerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = Summary
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ItemSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    material_type = serializers.CharField(source='project_material.material_type', read_only=True)
    
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class RecommendationSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    item_title = serializers.CharField(source='item.title', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Nested Serializers for detailed views
class ProjectDetailSerializer(serializers.ModelSerializer):
    materials = ProjectMaterialSerializer(many=True, read_only=True)
    items = ItemSerializer(many=True, read_only=True)
    summaries = SummarySerializer(many=True, read_only=True)
    recommendations = RecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProjectMaterialDetailSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    items = ItemSerializer(many=True, read_only=True)
    recommendations = RecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProjectMaterial
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
