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
]
