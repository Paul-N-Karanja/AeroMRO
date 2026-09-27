from django import forms

from .models import Aircraft, Part, Technician, WorkOrder


class AircraftForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = [
            "tail_number",
            "manufacturer_serial_number",
            "aircraft_type",
            "fuel_on_board_kg",
            "flight_hours",
            "flight_cycles",
            "last_maintenance",
            "next_maintenance",
            "seat_map",
            "status",
        ]


class TechnicianForm(forms.ModelForm):
    class Meta:
        model = Technician
        fields = [
            "technician_name",
            "technician_specialization",
            "technician_number",
            "technician_availability",
        ]


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = [
            "work_order_number",
            "work_order_description",
            "aircraft",
            "technician",
            "priority",
            "status",
            "scheduled_date",
            "due_date",
            "estimated_hours",
            "actual_hours",
        ]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = [
            "part_number",
            "part_description",
            "quantity_on_hand",
            "minimum_stock_level",
            "manufacturer",
            "location",
            "unit_cost",
        ]
