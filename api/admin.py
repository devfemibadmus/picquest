from django import forms
from django.db import models
from django.contrib import admin
from .models import Documents, Tasks, User, Token, UserTasks, History, Payments

@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'is_verify', 'file_url')
    search_fields = ('user__email',)
    list_filter = ('user__is_verify',)
    def user_email(self, obj):
        return obj.user.email
    def file_url(self, obj):
        return obj.theFile.url
    def is_verify(self, obj):
        return obj.user.is_verify
    is_verify.boolean = True

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ('amounts', 'title', 'description')
    search_fields = ('title',)
    formfield_overrides = {
        models.FloatField: {'widget': forms.NumberInput(attrs={'step': '0.1'})},
    }

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('dates', 'action', 'user', 'formatted_amount', 'description')
    search_fields = ('user', 'dates')
    list_filter = ('user__is_verify', 'dates')
    def formatted_amount(self, obj):
        return f"${obj.amount}"
    formatted_amount.short_description = 'Amount'

@admin.register(UserTasks)
class UserTasksAdmin(admin.ModelAdmin):
    list_display = ('task_title', 'status', 'created_at', 'user_email', 'is_verify')
    search_fields = ('task__title', 'user__email')
    list_filter = ('status', 'user__is_verify', 'created_at')
    def task_title(self, obj):
        return obj.task.title
    def user_email(self, obj):
        return obj.user.email
    def is_verify(self, obj):
        return obj.user.is_verify
    is_verify.boolean = True

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'balance', 'referral', 'is_verify', 'hasPaid', 'documentSubmitted')
    search_fields = ('email',)
    list_filter = ('is_verify', 'hasPaid', 'documentSubmitted')

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user_email', 'is_verify', 'hasPaid', 'documentSubmitted')
    search_fields = ('user__email',)
    def user_email(self, obj):
        return obj.user.email
    def hasPaid(self, obj):
        return obj.user.hasPaid
    def is_verify(self, obj):
        return obj.user.is_verify
    def documentSubmitted(self, obj):
        return obj.user.documentSubmitted
    hasPaid.boolean = True
    is_verify.boolean = True
    documentSubmitted.boolean = True

@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'reference', 'is_verify', 'hasPaid', 'documentSubmitted')
    search_fields = ('user__email',)
    def user_email(self, obj):
        return obj.user.email
    def hasPaid(self, obj):
        return obj.user.hasPaid
    def is_verify(self, obj):
        return obj.user.is_verify
    def documentSubmitted(self, obj):
        return obj.user.documentSubmitted
    hasPaid.boolean = True
    is_verify.boolean = True
    documentSubmitted.boolean = True



