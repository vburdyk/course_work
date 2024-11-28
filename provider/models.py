from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserBalance(models.Model):
    """Модель балансу для користувача"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"


class SubscriptionPlan(models.Model):
    """Модель тарифного плану для підписки"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  # дозволяємо пустий опис
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField()
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'subscription_plans'

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Модель підписки користувача"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,  # дозволяємо null для існуючих записів
        blank=True
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,  # дозволяємо null для існуючих записів
        blank=True
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)  # дозволяємо null
    status = models.CharField(
        max_length=20,
        choices=[
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
            ('Cancelled', 'Cancelled')
        ],
        default='Active'
    )
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'subscriptions'

    def __str__(self):
        return f"{self.user.username if self.user else 'No user'} - {self.plan.name if self.plan else 'No plan'}"


class Invoice(models.Model):
    """Модель рахунка для підписки користувача"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="invoices",
        null=True,  # дозволяємо null для існуючих записів
        blank=True
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="invoices",
        null=True,  # дозволяємо null для існуючих записів
        blank=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00  # значення за замовчуванням
    )
    due_date = models.DateField(default=timezone.now)
    paid = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'invoices'

    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        return f"Invoice #{self.id} - {status}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SupportTicket(models.Model):
    """Модель заявки на підтримку"""
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="support_tickets",
        null=True,  # дозволяємо null для існуючих записів
        blank=True
    )
    issue = models.TextField(blank=True)  # дозволяємо пустий текст
    status = models.CharField(
        max_length=20,
        default='Open',
        choices=STATUS_CHOICES
    )
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_tickets'

    def __str__(self):
        return f"Ticket #{self.id} - {self.status}"
