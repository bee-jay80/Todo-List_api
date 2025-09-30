from django.contrib import admin
from .models import Task

# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user')
    list_filter = ('completed', 'created_at', 'updated_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-created_at',)