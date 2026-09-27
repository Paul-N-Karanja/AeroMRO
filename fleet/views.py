from django.shortcuts import get_object_or_404, render, redirect
from .forms import WorkOrderForm
from .models import Aircraft, WorkOrder, Part
from django.db.models import F
from django.utils import timezone


def aircraft_list(request):
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    aircrafts = Aircraft.objects.all()

    if search_query:
        aircrafts = aircrafts.filter(tail_number__icontains=search_query)

    if status_filter:
        aircrafts = aircrafts.filter(status=status_filter)

    return render(
        request,
        "fleet/aircraft_list.html",
        {
            "aircrafts": aircrafts,
            "search_query": search_query,
            "status_filter": status_filter,
            "status_choices": Aircraft.Status.choices,
        },
    )


def aircraft_detail(request, aircraft_id):
    aircraft = get_object_or_404(
        Aircraft,
        id=aircraft_id,
    )

    work_orders = aircraft.work_orders.all()

    return render(
        request,
        "fleet/aircraft_detail.html",
        {
            "aircraft": aircraft,
            "work_orders": work_orders,
        },
    )


def work_order_list(request):
    work_orders = WorkOrder.objects.all().order_by("due_date")

    return render(
        request,
        "fleet/work_order_list.html",
        {
            "work_orders": work_orders,
        },
    )


def work_order_detail(request, pk):
    work_order = get_object_or_404(
        WorkOrder,
        pk=pk,
    )

    required_parts = work_order.required_parts.all()

    return render(
        request,
        "fleet/work_order_detail.html",
        {
            "work_order": work_order,
            "required_parts": required_parts,
        },
    )


def work_order_create(request):
    if request.method == "POST":
        form = WorkOrderForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("work_order_list")

    else:
        form = WorkOrderForm()

    return render(
        request,
        "fleet/work_order_form.html",
        {
            "form": form,
        },
    )


def part_list(request):
    parts = Part.objects.all().order_by("part_number")

    return render(
        request,
        "fleet/part_list.html",
        {
            "parts": parts,
        },
    )


def dashboard(request):

    today = timezone.localdate()

    aircraft_total = Aircraft.objects.count()

    aircraft_active = Aircraft.objects.filter(
        status__in=[
            Aircraft.Status.ON_GROUND,
            Aircraft.Status.IN_FLIGHT,
        ]
    ).count()

    aircraft_maintenance = Aircraft.objects.filter(
        status=Aircraft.Status.MAINTENANCE
    ).count()

    aircraft_grounded = Aircraft.objects.filter(status=Aircraft.Status.GROUNDED).count()

    open_work_orders = WorkOrder.objects.filter(
        status__in=[
            WorkOrder.Status.OPEN,
            WorkOrder.Status.IN_PROGRESS,
        ]
    ).count()

    overdue_work_orders = (
        WorkOrder.objects.filter(due_date__lt=today)
        .exclude(
            status__in=[
                WorkOrder.Status.COMPLETED,
                WorkOrder.Status.CANCELLED,
            ]
        )
        .count()
    )

    low_stock_parts = Part.objects.filter(
        quantity_on_hand__lte=F("minimum_stock_level")
    ).count()

    recent_work_orders = WorkOrder.objects.order_by("-created_at")[:5]

    return render(
        request,
        "fleet/dashboard.html",
        {
            "aircraft_total": aircraft_total,
            "aircraft_active": aircraft_active,
            "aircraft_maintenance": aircraft_maintenance,
            "aircraft_grounded": aircraft_grounded,
            "open_work_orders": open_work_orders,
            "overdue_work_orders": overdue_work_orders,
            "low_stock_parts": low_stock_parts,
            "recent_work_orders": recent_work_orders,
        },
    )
