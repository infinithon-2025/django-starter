from django.db import models


class Project(models.Model):
    author_email = models.EmailField()
    project_name = models.CharField(max_length=255)
    project_code = models.CharField(max_length=255)
    project_keyword = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name} ({self.author_email})"

    class Meta:
        db_table = 'projects'


class ProjectMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('jira', 'Jira'),
        ('slack', 'Slack'),
        ('github', 'Github'),
        ('gmail', 'Gmail'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='materials')
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES)
    material_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material_type} - {self.project.project_name}"

    class Meta:
        db_table = 'project_materials'


class AIRequest(models.Model):
    input = models.TextField()
    output = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Request {self.id} - {self.created_at}"

    class Meta:
        db_table = 'ai_requests'


class Summary(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='summaries')
    ai_request = models.ForeignKey(AIRequest, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.project.project_name}"

    class Meta:
        db_table = 'summaries'


class Item(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='items')
    project_material = models.ForeignKey(ProjectMaterial, on_delete=models.CASCADE, related_name='items')
    channel_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    body = models.TextField()
    link = models.URLField()
    is_fixed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    origin_data_created_at = models.DateTimeField(auto_now=True)
    origin_data_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.channel_name}"

    class Meta:
        db_table = 'items'


class Recommendation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='recommendations')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='recommendations')
    project_material = models.ForeignKey(ProjectMaterial, on_delete=models.CASCADE, related_name='recommendations', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recommendation for {self.item.title}"

    class Meta:
        db_table = 'recommendations'
