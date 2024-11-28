from django.contrib import admin
from .models import Subscription, SubscriptionPlan, Invoice, SupportTicket, UserBalance

admin.site.register(Subscription)
admin.site.register(SubscriptionPlan)
admin.site.register(Invoice)
admin.site.register(SupportTicket)
admin.site.register(UserBalance)

