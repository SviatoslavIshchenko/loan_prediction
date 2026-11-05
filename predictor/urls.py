from django.urls import path
from . import views

urlpatterns = [
    path("", views.predict_loan, name="predict"),
    path("history/", views.history, name="history"),
    path(
        "feature-importance/",
        views.feature_importance,
        name="feature_importance"
    ),
    path(
        "history/<int:prediction_id>/",
        views.prediction_detail,
        name="prediction_detail"
    ),
    path("export/csv/", views.export_csv, name="export_csv"),

    path("export/excel/", views.export_excel, name="export_excel"),
]
