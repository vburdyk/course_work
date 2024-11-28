from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

from .models import Subscription, Invoice, SupportTicket, SubscriptionPlan, UserBalance


def not_authenticated(user):
    return not user.is_authenticated


@user_passes_test(not_authenticated, login_url='dashboard')
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard or another page
        else:
            messages.error(request, 'Неправильний логін або пароль')

    return render(request, 'login.html')


@user_passes_test(not_authenticated, login_url='dashboard')
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Паролі не співпадають.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Користувач з таким логіном вже існує.')
            return redirect('register')

        user = User.objects.create_user(username=username, password=password1)
        user.save()

        messages.success(request, 'Реєстрація пройшла успішно! Тепер ви можете увійти.')
        return redirect('login')

    return render(request, 'register.html')


@login_required(login_url='login')
def dashboard(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    subscription_plans = SubscriptionPlan.objects.all()
    invoices = Invoice.objects.filter(user=request.user)
    tickets = SupportTicket.objects.filter(user=request.user)

    try:
        user_balance = UserBalance.objects.get(user=request.user)
    except UserBalance.DoesNotExist:
        user_balance = None

    active_subscription_plan_id = None
    active_subscription = subscriptions.filter(status='Active').first()
    if active_subscription:
        active_subscription_plan_id = active_subscription.plan.id

    return render(request, 'dashboard.html', {
        'subscriptions': subscriptions,
        'subscriptions_plans': subscription_plans,
        'invoices': invoices,
        'tickets': tickets,
        'user_balance': user_balance,
        'active_subscription_plan_id': active_subscription_plan_id,

    })


@login_required(login_url='login')
def new_ticket(request):
    if request.method == 'POST':
        issue = request.POST.get('issue')
        SupportTicket.objects.create(user=request.user, issue=issue)
        return redirect('dashboard')
    return render(request, 'new_ticket.html')


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def add_subscription_plan(request):
    if request.method == 'POST':
        plan_name = request.POST.get('plan_name')
        plan_description = request.POST.get('plan_description')
        price = request.POST.get('price')
        duration_months = request.POST.get('duration')

        if plan_name and price and duration_months:
            SubscriptionPlan.objects.create(
                name=plan_name,
                description=plan_description,
                price=float(price),
                duration_months=int(duration_months)
            )
            return redirect('dashboard')  # Перенаправлення на список підписок

    return render(request, 'add_subscription_plan.html')


@login_required(login_url='login')
def subscribe(request, plan_id):
    plan = SubscriptionPlan.objects.get(id=plan_id)

    try:
        user_balance = UserBalance.objects.get(user=request.user)
    except UserBalance.DoesNotExist:
        user_balance = UserBalance.objects.create(user=request.user, balance=0.0)

    if user_balance.balance >= plan.price:
        user_balance.balance -= plan.price
        user_balance.save()

        existing_subscription = Subscription.objects.filter(user=request.user).first()
        if existing_subscription:
            existing_subscription.delete()

        new_subscription = Subscription(
            user=request.user,
            plan=plan,  # Вказуємо план
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=plan.duration_months * 30),  # Тривалість плану
            status='Active'
        )
        new_subscription.save()

        new_invoice = Invoice(
            user=request.user,
            amount=plan.price,
            due_date=datetime.now().date() + timedelta(days=30),  # Рахунок до кінця місяця
            paid=True  # Статус оплачено
        )
        new_invoice.save()

        messages.success(request, 'Ви успішно підписалися на новий план!')
    else:
        messages.error(request, 'Недостатньо коштів на балансі для підписки на цей план.')

    return redirect('dashboard')


@staff_member_required(login_url='login')
def manage_tickets(request):
    open_tickets = SupportTicket.objects.filter(status='Open')
    in_progress_tickets = SupportTicket.objects.filter(status='In Progress')
    resolved_tickets = SupportTicket.objects.filter(status='Resolved')

    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        new_status = request.POST.get('status')
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
            ticket.status = new_status
            ticket.save()
        except SupportTicket.DoesNotExist:
            pass

    return render(request, 'manage_tickets.html', {
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets
    })
