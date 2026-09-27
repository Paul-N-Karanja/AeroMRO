from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path(
        "aircraft/",
        views.aircraft_list,
        name="aircraft_list",
    ),
    path(
        "aircraft/<int:aircraft_id>/",
        views.aircraft_detail,
        name="aircraft_detail",
    ),
    path(
        "work-orders/",
        views.work_order_list,
        name="work_order_list",
    ),
    path(
        "work-orders/create/",
        views.work_order_create,
        name="work_order_create",
    ),
    path(
        "work-orders/<int:pk>/",
        views.work_order_detail,
        name="work_order_detail",
    ),
    path(
        "parts/",
        views.part_list,
        name="part_list",
    ),
]
