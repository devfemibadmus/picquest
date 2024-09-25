from django import forms
from django.db import models
from django.contrib import admin
from collections import defaultdict
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, OuterRef, Subquery
from .models import Document, Task, User, Token, UserTask, PayOut, VerificationFee, BankList



class DocumentAdminFilter(SimpleListFilter):
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

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_is_verify', 'gov_id', 'stu_id')
    search_fields = ('user__email',)
    list_filter = ('user__is_verify', DocumentAdminFilter)
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

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('amounts', 'title', 'description')
    search_fields = ('title',)
    formfield_overrides = {
        models.FloatField: {'widget': forms.NumberInput(attrs={'step': '0.1'})},
    }

@admin.register(PayOut)
class PayOutAdmin(admin.ModelAdmin):
    list_display = ('dates', 'action', 'user', 'formatted_amount', 'description', 'checkout')
    search_fields = ('user', 'dates')
    list_filter = ('user__is_verify', 'dates', 'checkout')
    actions = ['cancel_withdraw', 'referral_credited', 'paid_user', 'tasks_credited']

    def formatted_amount(self, obj):
        return f"${obj.amount}"
    formatted_amount.short_description = 'Amount'

    def referral_credited(self, request, queryset):
        user_balances = defaultdict(float)
        for payout in queryset:
            if not payout.checkout:
                if 'Credit for Referral will be added to your account' in payout.description:
                    payout.action = 'credit referral'
                    payout.checkout = True
                    user_balances[payout.user] += payout.amount
                    payout.save()
        for user, balance_increase in user_balances.items():
            user.balance += balance_increase
            user.save()
        self.message_user(request, "Selected payouts have been marked as referral creditted.")
    def tasks_credited(self, request, queryset):
        user_balances = defaultdict(float)
        for payout in queryset:
            if not payout.checkout:
                if 'Credit for the tasks you’ve completed is pending' in payout.description:
                    payout.action = 'credit'
                    payout.checkout = True
                    user_balances[payout.user] += payout.amount
                    payout.save()
        for user, balance_increase in user_balances.items():
            user.balance += balance_increase
            user.save()
        self.message_user(request, "Selected payouts have been marked as tasks creditted.")
    def cancel_withdraw(self, request, queryset):
        user_balances = defaultdict(float)
        for payout in queryset:
            if not payout.checkout:
                if payout.action == 'pending debit':
                    user_balances[payout.user] += payout.amount
                    payout.delete()
        for user, balance_increase in user_balances.items():
            user.balance += balance_increase
            user.save()
        self.message_user(request, "Selected payouts have been marked as cancelled.")
    def paid_user(self, request, queryset):
        user_balances = defaultdict(float)
        for payout in queryset:
            if not payout.checkout:
                if 'withdraw' in payout.description:
                    payout.action = 'debit'
                    payout.checkout = True
                    payout.save()
        self.message_user(request, "Selected payouts have been marked as paid.")

    cancel_withdraw.short_description = 'Cancelled selected Withdraws'
    referral_credited.short_description = 'Credit selected referrals'
    tasks_credited.short_description = 'Credit selected tasks'
    paid_user.short_description = 'Mark selected as Paid'

@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('task_title', 'created_at', 'user_email', 'photo_display')
    search_fields = ('task__title', 'user__email')
    list_filter = ('user__is_verify', 'created_at')
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
            PayOut.objects.create(user=obj.user, action='pending credit', amount=obj.task.amount)
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
    exclude = ('password', 'last_name', 'groups', 'is_staff', 'last_login', 'user_permissions', 'is_superuser', 'is_active')

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

class UsageFilter(SimpleListFilter):
    title = 'Bank Usage'
    parameter_name = 'usage'

    def lookups(self, request, model_admin):
        return [
            ('most_used', 'Most Used'),
            ('least_used', 'Least Used'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'most_used':
            most_used_bank = PayOut.objects.values('bankcode').annotate(usage_count=Count('bankcode')).order_by('-usage_count').first()
            if most_used_bank:
                return queryset.filter(code=most_used_bank['bankcode'])
        elif self.value() == 'least_used':
            least_used_bank = PayOut.objects.values('bankcode').annotate(usage_count=Count('bankcode')).order_by('usage_count').first()
            if least_used_bank:
                return queryset.filter(code=least_used_bank['bankcode'])
        return queryset

@admin.register(BankList)
class BankListAdmin(admin.ModelAdmin):
    exclude = ('code',)
    search_fields = ('name',)
    list_display = ('name', 'time_used')
    list_filter = (UsageFilter, )

    def time_used(self, obj):
        return PayOut.objects.filter(bankcode=obj.code).count()
    time_used.short_description = 'Times Used'
