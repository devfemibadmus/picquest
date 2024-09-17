from django import forms
from django.db import models
from django.contrib import admin
from django.utils.html import format_html
from .models import Documents, Tasks, User, Token, UserTasks, PayOut, VerificationFee

from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter

class UserTasksAdminFilter(SimpleListFilter):
    title = _('Photo Deleted')
    parameter_name = 'is_photo_deleted'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(photo='')
        if self.value() == 'no':
            return queryset.exclude(photo='')

class DocumentsAdminFilter(SimpleListFilter):
    title = _('File Deleted')
    parameter_name = 'is_files_deleted'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(govID='', stuID='')
        if self.value() == 'no':
            return queryset.exclude(govID='', stuID='')

@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_is_verify', 'gov_id', 'stu_id')
    search_fields = ('user__email',)
    list_filter = ('user__is_verify', DocumentsAdminFilter)
    actions = ['verify_user', 'un_verified']

    def user_email(self, obj):
        return obj.user.email

    def user_is_verify(self, obj):
        return obj.user.is_verify

    def gov_id(self, obj):
        if obj.govID:
            return format_html('<a href="{}" target="_blank"><img src="{}" alt="Image cannot be displayed" width="50" height="50" /></a>', obj.govID.url, obj.govID.url)
        return "File Deleted"
    
    def stu_id(self, obj):
        if obj.stuID:
            return format_html('<a href="{}" target="_blank"><img src="{}" alt="Image cannot be displayed" width="50" height="50" /></a>', obj.stuID.url, obj.stuID.url)
        return "File Deleted"

    def un_verified(self, request, queryset):
        for obj in queryset:
            if obj.govID:
                obj.user.is_verify = False
                obj.user.documentSubmitted = False
                obj.user.save()
                obj.govID.delete(save=False)
                obj.stuID.delete(save=False)
                obj.govID = None
                obj.stuID = None
                obj.delete()
        self.message_user(request, "Selected documents have been unverified.")

    def verify_user(self, request, queryset):
        for obj in queryset:
            if obj.govID:
                obj.user.is_verify = True
                obj.user.documentSubmitted = True
                obj.user.save()
                obj.delete()
        self.message_user(request, "Selected documents have been verified.")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    user_is_verify.boolean = True
    gov_id.short_description = "Gov ID"
    stu_id.short_description = "Student ID"
    user_is_verify.short_description = "Verified User"
    verify_user.short_description = "Verify selected documents"
    un_verified.short_description = "Unverified selected documents"

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ('amounts', 'title', 'description')
    search_fields = ('title',)
    formfield_overrides = {
        models.FloatField: {'widget': forms.NumberInput(attrs={'step': '0.1'})},
    }

@admin.register(PayOut)
class PayOutAdmin(admin.ModelAdmin):
    list_display = ('dates', 'action', 'user', 'formatted_amount', 'description')
    search_fields = ('user', 'dates')
    list_filter = ('user__is_verify', 'dates')
    def formatted_amount(self, obj):
        return f"${obj.amount}"
    formatted_amount.short_description = 'Amount'

@admin.register(UserTasks)
class UserTasksAdmin(admin.ModelAdmin):
    list_display = ('task_title', 'created_at', 'user_email', 'photo_display')
    search_fields = ('task__title', 'user__email')
    list_filter = ('user__is_verify', 'created_at', UserTasksAdminFilter)
    actions = ['fail_task', 'pass_task']

    def task_title(self, obj):
        return obj.task.title

    def user_email(self, obj):
        return obj.user.email
 
    def fail_task(self, request, queryset):
        for obj in queryset:
            obj.user.pendTasks -=1
            obj.user.failTasks +=1
            obj.user.save()
            obj.delete()
        self.message_user(request, 'Selected user tasks has failed')
    
    def pass_task(self, request, queryset):
        for obj in queryset:
            obj.user.pendTasks -=1
            obj.user.passTasks +=1
            obj.user.save()
            obj.delete()
        PayOutobjects.create(user=obj.user, action='pending credit', amount=obj.task.amount)
        self.message_user(request, 'Selected user tasks has passed')

    def photo_display(self, obj):
        if obj.photo:
            return format_html('<a href="{}" target="_blank"><img src="{}" alt="Image cannot be displayed" width="50" height="50" /></a>', obj.photo.url, obj.photo.url)
        return "Photo Deleted"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    photo_display.short_description = "Photo"
    fail_task.short_description = "Fail selected tasks"
    pass_task.short_description = "Pass selected tasks"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'pendTasks', 'failTasks', 'passTasks', 'balance', 'is_verify', 'hasPaid', 'documentSubmitted')
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

@admin.register(VerificationFee)
class VerificationFeeAdmin(admin.ModelAdmin):
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



