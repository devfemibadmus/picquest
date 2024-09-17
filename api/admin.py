from django import forms
from django.db import models
from django.contrib import admin
from django.utils.html import format_html
from .models import Documents, Tasks, User, Token, UserTasks, History, Payments

import zipfile
from django.http import HttpResponse
from io import BytesIO
import requests

@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_is_verify', 'is_downloaded', 'file_display')
    search_fields = ('user__email',)
    list_filter = ('user__is_verify',)
    actions = ['delete_file', 'download_files']

    def user_email(self, obj):
        return obj.user.email

    def user_is_verify(self, obj):
        return obj.user.is_verify
    user_is_verify.boolean = True
    user_is_verify.short_description = "Verified User"

    def delete_file(self, request, queryset):
        for obj in queryset:
            if obj.theFile:
                obj.theFile.delete(save=False)
                obj.theFile = None
                obj.save()
        self.message_user(request, "Selected files have been deleted.")
    delete_file.short_description = "Delete selected files"

    def download_files(self, request, queryset):
        files_to_download = []
        for obj in queryset:
            if obj.theFile and not obj.is_downloaded:
                files_to_download.append(obj.theFile.url)
                obj.is_downloaded = True
                obj.save()

        if files_to_download:
            # Create a zip file in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for file_url in files_to_download:
                    response = requests.get(file_url)
                    file_name = file_url.split('/')[-1]  # Extract file name from URL
                    zip_file.writestr(file_name, response.content)

            zip_buffer.seek(0)

            # Send the zip file as a response
            response = HttpResponse(zip_buffer, content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename="documents.zip"'
            return response

        self.message_user(request, "No files to download.")
    download_files.short_description = "Download selected files (if not downloaded)"

    def file_display(self, obj):
        if obj.theFile:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.theFile.url)
        return "File Deleted"
    file_display.short_description = "File"



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
    list_display = ('task_title', 'status', 'created_at', 'user_email', 'is_verify', 'photo_display')
    search_fields = ('task__title', 'user__email')
    list_filter = ('status', 'user__is_verify', 'created_at')
    actions = ['delete_photo']

    def task_title(self, obj):
        return obj.task.title

    def user_email(self, obj):
        return obj.user.email

    def is_verify(self, obj):
        return obj.user.is_verify
    is_verify.boolean = True

    def delete_photo(self, request, queryset):
        for obj in queryset:
            if obj.photo:
                obj.photo.delete(save=False)
                obj.photo = None
                obj.save()
        self.message_user(request, "Selected photos have been deleted.")
    delete_photo.short_description = "Delete selected photos"

    def photo_display(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" />', obj.photo.url)
        return "Photo Deleted"
    photo_display.short_description = "Photo"

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



