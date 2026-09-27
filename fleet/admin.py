from django.contrib import admin
from .models import (
    Aircraft,
    Technician,
    WorkOrder,
    Part,
    InventoryTransaction,
    WorkOrderPart,
)

# admin.site.register(Aircraft)
# admin.site.register(Technician)
# admin.site.register(WorkOrder)
# admin.site.register(Part)
# admin.site.register(InventoryTransaction)
# admin.site.register(WorkOrderPart)


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = (
        "tail_number",
        "aircraft_type",
        "status",
        "flight_hours",
        "flight_cycles",
        "next_maintenance",
    )

    list_filter = (
        "status",
        "aircraft_type",
    )

    search_fields = (
        "tail_number",
        "manufacturer_serial_number",
        "aircraft_type",
    )

    ordering = ("tail_number",)


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = (
        "technician_number",
        "technician_name",
        "technician_specialization",
        "technician_availability",
    )

    list_filter = (
        "technician_specialization",
        "technician_availability",
    )

    search_fields = (
        "technician_number",
        "technician_name",
    )

    ordering = ("technician_name",)


class WorkOrderPartInline(admin.TabularInline):
    model = WorkOrderPart
    extra = 1

    fields = (
        "part",
        "quantity_required",
        "quantity_used",
        "notes",
    )


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "work_order_number",
        "aircraft",
        "technician",
        "priority",
        "status",
        "scheduled_date",
        "due_date",
        "estimated_hours",
        "actual_hours",
    )

    list_filter = (
        "priority",
        "status",
        "scheduled_date",
        "due_date",
    )

    search_fields = (
        "work_order_number",
        "work_order_description",
        "aircraft__tail_number",
        "technician__technician_name",
    )

    ordering = ("due_date",)

    inlines = (WorkOrderPartInline,)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = (
        "part_number",
        "part_description",
        "manufacturer",
        "quantity_on_hand",
        "minimum_stock_level",
        "location",
        "unit_cost",
    )

    list_filter = (
        "manufacturer",
        "location",
    )

    search_fields = (
        "part_number",
        "part_description",
        "manufacturer",
    )

    ordering = ("part_number",)


@admin.register(WorkOrderPart)
class WorkOrderPartAdmin(admin.ModelAdmin):
    list_display = (
        "work_order",
        "part",
        "quantity_required",
        "quantity_used",
    )

    search_fields = (
        "work_order__work_order_number",
        "part__part_number",
    )


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "part",
        "transaction_type",
        "quantity",
        "work_order",
        "technician",
        "transaction_date",
        "reference",
    )

    list_filter = (
        "transaction_type",
        "transaction_date",
    )

    search_fields = (
        "part__part_number",
        "reference",
        "work_order__work_order_number",
        "technician__technician_number",
    )

    ordering = ("-transaction_date",)
