# Pic Quest

Check out app [devfemibadmus/picquestf](https://github.com/devfemibadmus/picquestf) Django admin is cool, but what’s even cooler is supercharging it to make you feel like the ultimate admin overlord—like, 'Oh yeah, I'm the admin; I can click all the things!' 😂, below are some explanation/code.


## Views

- **Registration/Login**: Handles user signup and login, ensuring unique emails.
- **Data Retrieval**: Retrieves user info and updates authentication tokens.

- **Payment Integration**: Uses Paystack API for secure payments and verifies transactions.
- **Payout Management**: Manages user payouts and referral bonuses.

- **Token Management**: Regularly updates session tokens for enhanced security.
- **Error Handling**: Provides appropriate error responses.

- **Task Retrieval**: Retrieves user-assigned tasks for the current day, including counts of completed tasks and available tasks based on the user's daily limit.  
- **Available Tasks**: Provides a list of tasks not yet assigned to the user, randomly selected up to the remaining limit for the day.


## Admin

- **Document Management**: Administers user-submitted documents, allowing verification and unverification of documents based on provided government and student IDs. Includes custom filters to show deleted files and user verification status.

- **Payout Management**: Handles financial transactions and payouts, including the ability to credit users for referrals and completed tasks. Manages withdrawal cancellations and tracks user balances based on various payout actions.

- **User Task Management**: Oversees tasks assigned to users, with the ability to mark tasks as failed or passed. Updates user task statistics and manages payouts for successfully completed tasks.

- **User Administration**: Manages user accounts and their details, including task counts and payment statuses. Excludes sensitive information from the admin display.

- **Token and Verification Management**: Displays user tokens and verification fees, allowing admins to view verification and payment statuses directly linked to users.

- **Bank List Management**: Administers the list of banks, including tracking usage frequency through custom filters that categorize banks by their usage in payout transactions.


**Filters**

```python
class UsageFilter(SimpleListFilter):
    title = 'Bank Usage'  # Label for the filter in the admin UI
    parameter_name = 'usage'  # Query parameter for the filter

    def lookups(self, request, model_admin):
        # Define options for the filter: Most Used and Least Used
        return [
            ('most_used', 'Most Used'),
            ('least_used', 'Least Used'),
        ]

    def queryset(self, request, queryset):
        # Filter queryset based on the selected usage option
        if self.value() == 'most_used':
            most_used_bank = PayOut.objects.values('bankcode').annotate(usage_count=Count('bankcode')).order_by('-usage_count').first()
            if most_used_bank:
                return queryset.filter(code=most_used_bank['bankcode'])
        elif self.value() == 'least_used':
            least_used_bank = PayOut.objects.values('bankcode').annotate(usage_count=Count('bankcode')).order_by('usage_count').first()
            if least_used_bank:
                return queryset.filter(code=least_used_bank['bankcode'])
        return queryset  # Return the original queryset if no filter is applied
```

**Payout**

```python
@admin.register(PayOut)
class PayOutAdmin(admin.ModelAdmin):
    list_display = ('dates', 'action', 'user', 'formatted_amount', 'description', 'checkout')  # Columns to display in the admin list view
    search_fields = ('user', 'dates')  # Fields to enable search functionality in the admin
    list_filter = ('user__is_verify', 'dates', 'checkout')  # Filters for refining the list of records
    actions = ['cancel_withdraw', 'referral_credited', 'paid_user', 'tasks_credited']  # Custom actions available in the admin interface

    def formatted_amount(self, obj):
        # Format the payout amount with a dollar sign for better readability
        return f"${obj.amount}"
    formatted_amount.short_description = 'Amount'  # Column label for formatted amount

    def referral_credited(self, request, queryset):
        # Iterate through the selected payouts to credit users for referrals
        user_balances = defaultdict(float)  # Dictionary to keep track of user balance updates
        for payout in queryset:
            # Process only unchecked payouts
            if not payout.checkout:
                # Check if the description indicates a referral credit
                if 'Credit for Referral will be added to your account' in payout.description:
                    payout.action = 'credit referral'  # Update action to indicate a referral credit
                    payout.checkout = True  # Mark the payout as processed
                    user_balances[payout.user] += payout.amount  # Accumulate the credit to the user's balance
                    payout.save()  # Save the updated payout record
        # Update the balances of all affected users based on accumulated credits
        for user, balance_increase in user_balances.items():
            user.balance += balance_increase  # Increase the user's balance
            user.save()  # Save the updated user record
        self.message_user(request, "Selected payouts have been marked as referral credited.")  # Notify admin

    def tasks_credited(self, request, queryset):
        # Iterate through the selected payouts to credit users for completed tasks
        user_balances = defaultdict(float)  # Dictionary to track balance increases for users
        for payout in queryset:
            if not payout.checkout:  # Process only unchecked payouts
                # Check if the description indicates a task credit
                if 'Credit for the tasks you’ve completed is pending' in payout.description:
                    payout.action = 'credit'  # Update action to indicate a task credit
                    payout.checkout = True  # Mark the payout as processed
                    user_balances[payout.user] += payout.amount  # Add to the user's balance
                    payout.save()  # Save the updated payout record
        # Update the balances of all affected users
        for user, balance_increase in user_balances.items():
            user.balance += balance_increase  # Increase the user's balance
            user.save()  # Save the updated user record
        self.message_user(request, "Selected payouts have been marked as tasks credited.")  # Notify admin

    def cancel_withdraw(self, request, queryset):
        # Cancel selected withdrawals and restore balances to users
        user_balances = defaultdict(float)  # Dictionary to track restored balances
        for payout in queryset:
            if not payout.checkout:  # Process only unchecked payouts
                if payout.action == 'pending debit':  # Check if the action indicates a pending withdrawal
                    user_balances[payout.user] += payout.amount  # Accumulate the withdrawal amount to restore to the user
                    payout.delete()  # Remove the payout record since it's cancelled
        # Restore the balances for each affected user
        for user, balance_increase in user_balances.items():
            user.balance += balance_increase  # Increase the user's balance
            user.save()  # Save the updated user record
        self.message_user(request, "Selected payouts have been marked as cancelled.")  # Notify admin

    def paid_user(self, request, queryset):
        # Mark selected payouts as paid and update user records
        for payout in queryset:
            if not payout.checkout:  # Process only unchecked payouts
                if 'withdraw' in payout.description:  # Check if the description indicates a withdrawal
                    payout.action = 'debit'  # Update action to indicate a debit (payment)
                    payout.checkout = True  # Mark the payout as processed
                    payout.save()  # Save the updated payout record
        self.message_user(request, "Selected payouts have been marked as paid.")  # Notify admin

    # Short descriptions for actions to display in the admin UI
    cancel_withdraw.short_description = 'Cancel selected Withdraws'
    referral_credited.short_description = 'Credit selected referrals'
    tasks_credited.short_description = 'Credit selected tasks'
    paid_user.short_description = 'Mark selected as Paid'
```

#### more? check api/admin.py

## Production Setup

1. Clone the repositories:
   - App: `git clone https://github.com/devfemibadmus/picquestf`
   - Website: `git clone https://github.com/devfemibadmus/picquest`

2. Build the Flutter web app:
   ```bash
   cd picquestf
   flutter build web
   ```

3. Copy the built web app to your Django project:
   ```bash
   cp -r build/web ../picquest/static/app
   ```

4. Continue with your Django settings configuration.

