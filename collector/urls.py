from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),

    # Email verification
    path(
        "accounts/verify/<int:user_id>/",
        views.verify_email_token,
        name="verify_email_token",
    ),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("spaces/new/", views.space_create, name="space_create"),
    path("spaces/<slug:slug>/settings/", views.space_edit, name="space_edit"),
    path(
        "dashboard/testimonials/<int:pk>/<str:action>/",
        views.testimonial_action,
        name="testimonial_action",
    ),
    path("collect/<slug:slug>/", views.collect_testimonial, name="collect_testimonial"),
    path("collect/<slug:slug>/thanks/", views.collect_thanks, name="collect_thanks"),
    path("wall/<slug:slug>/", views.wall, name="wall"),
    path("embed/<slug:slug>/", views.embed_widget, name="embed_widget"),
]