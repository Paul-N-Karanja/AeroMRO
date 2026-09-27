from django.db import models
from decimal import Decimal
from django.utils import timezone


class Aircraft(models.Model):
    class Status(models.TextChoices):
        ON_GROUND = "ON_GROUND", "On Ground (Available)"
        IN_FLIGHT = "IN_FLIGHT", "In Flight"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        GROUNDED = "GROUNDED", "Grounded"
        RETIRED = "RETIRED", "Retired / Decommissioned"

    tail_number = models.CharField(
        max_length=20, unique=True
    )  # plane license plate given by aviation authority
    manufacturer_serial_number = models.CharField(
        max_length=20
    )  # permanent builder assigned ID
    aircraft_type = models.CharField(
        max_length=50
    )  # specify distinct models for air traffic control and flight planning

    fuel_on_board_kg = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    flight_hours = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )  # time an aircraft has spent from the moment its wheels leave the ground during takeoff to the moment they touch down upon landing

    flight_cycles = (
        models.PositiveIntegerField()
    )  # one complete takeoff and landing sequence

    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seat_map = models.JSONField(
        default=dict, blank=True
    )  # identifies seat layout inside an aircraft

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ON_GROUND
    )

    @property
    def is_operational(self):
        return self.status in {
            self.Status.ON_GROUND,
            self.Status.IN_FLIGHT,
        }

    def __str__(self):
        return f"{self.tail_number} - {self.aircraft_type}"


class Technician(models.Model):
    class Specialization(models.TextChoices):
        AIRFRAME = "AIRFRAME", "Airframe & Structural Mechanics"
        AVIONICS = "AVIONICS", "Avionics & Electrical Systems"
        POWERPLANT = "POWERPLANT", "Powerplant & Propulsion"
        HYDRAULICS = "HYDRAULICS", "Hydraulics & Mechanical Systems"
        GENERAL = "GENERAL", "General"

    class Availability(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        BUSY = "BUSY", "Busy"
        LEAVE = "LEAVE", "On Leave"
        INACTIVE = "INACTIVE", "Inactive"

    technician_name = models.CharField(max_length=100, default="Unknown Technician")
    technician_specialization = models.CharField(
        choices=Specialization.choices, max_length=20, default=Specialization.GENERAL
    )
    technician_number = models.CharField(max_length=20, unique=True, default="TECH-000")
    technician_availability = models.CharField(
        choices=Availability.choices, max_length=20, default=Availability.AVAILABLE
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.technician_number} - {self.technician_name} - {self.technician_specialization}"


class WorkOrder(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    work_order_number = models.CharField(max_length=20, unique=True)
    work_order_description = models.TextField()

    aircraft = models.ForeignKey(
        Aircraft, on_delete=models.PROTECT, related_name="work_orders"
    )
    technician = models.ForeignKey(
        Technician, on_delete=models.PROTECT, related_name="work_orders"
    )
    parts = models.ManyToManyField(
        "Part", through="WorkOrderPart", related_name="work_orders", blank=True
    )
    priority = models.CharField(
        choices=Priority.choices, max_length=20, default=Priority.MEDIUM
    )
    status = models.CharField(
        choices=Status.choices, max_length=20, default=Status.OPEN
    )

    scheduled_date = models.DateField()  # when to perform the work
    due_date = models.DateField()
    estimated_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )
    actual_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_overdue(self):
        return self.due_date < timezone.localdate() and self.status not in {
            self.Status.COMPLETED,
            self.Status.CANCELLED,
        }

    def __str__(self):
        return f"{self.work_order_number} - {self.work_order_description}"


class Part(models.Model):
    part_number = models.CharField(max_length=20, unique=True)
    part_description = models.TextField()
    quantity_on_hand = models.PositiveIntegerField(default=0)
    minimum_stock_level = models.PositiveIntegerField(default=0)
    manufacturer = models.CharField(max_length=20)
    location = models.CharField(max_length=100, blank=True)
    unit_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.minimum_stock_level

    def __str__(self):
        return f"{self.part_number}\n{self.part_description}\nQuantity on hand: {self.quantity_on_hand}"


class WorkOrderPart(models.Model):
    part = models.ForeignKey(
        Part, on_delete=models.PROTECT, related_name="work_order_requirements"
    )
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.PROTECT, related_name="required_parts"
    )
    quantity_required = models.PositiveIntegerField(default=1)
    quantity_used = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["work_order", "part"], name="unique_work_order_part"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity_used__lte=models.F("quantity_required")),
                name="quantity_used_not_greater_than_required",
            ),
        ]

    @property
    def shortage_quantity(self):
        return max(
            self.quantity_required - self.part.quantity_on_hand,
            0,
        )

    @property
    def parts_available(self):
        return self.part.quantity_on_hand >= self.quantity_required

    def __str__(self):
        return f"{self.work_order.work_order_number}\n{self.part.part_number}\nRequired: {self.quantity_required}"


class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase Receipt"
        ISSUE = "ISSUE", "Issued to Work Order"
        RETURN = "RETURN", "Return to Stock"
        SCRAP = "SCRAP", "Scrapped / Condemned"

    part = models.ForeignKey(
        Part, on_delete=models.PROTECT, related_name="transactions"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.PROTECT,
        related_name="inventory_transactions",
        null=True,
        blank=True,
    )
    technician = models.ForeignKey(
        Technician,
        on_delete=models.PROTECT,
        related_name="inventory_transactions",
        null=True,
        blank=True,
    )
    transaction_type = models.CharField(choices=TransactionType.choices, max_length=20)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(blank=True, max_length=100)
    transaction_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Part: {self.part}\nType: {self.transaction_type} \nQuantity: {self.quantity} - "
