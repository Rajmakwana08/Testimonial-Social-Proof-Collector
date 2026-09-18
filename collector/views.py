from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .forms import SignUpForm, SpaceForm, TestimonialForm
from .models import Profile, Space, Testimonial


def home(request):
    return redirect("dashboard" if request.user.is_authenticated else "login")


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user.email = form.cleaned_data["email"]
        user.save(update_fields=["email"])
        Profile.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, "Your account is ready. Use the verification link to simulate confirming your email.")
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def verify_email(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.email_verified = True
    profile.save(update_fields=["email_verified"])
    messages.success(request, "Email verified. Your Proofly account is all set.")
    return redirect("dashboard")


@login_required
def dashboard(request):
    spaces = request.user.spaces.all()
    if not spaces.exists():
        messages.info(request, "Create your first collection Space to start receiving testimonials.")
        return redirect("space_create")

    selected_slug = request.GET.get("space")
    space = spaces.filter(slug=selected_slug).first() if selected_slug else spaces.first()
    if space is None:
        raise Http404("Space not found")

    status = request.GET.get("status", "all")
    search = request.GET.get("q", "").strip()
    rating = request.GET.get("rating", "")
    testimonials = space.testimonials.all()
    if status in dict(Testimonial.Status.choices):
        testimonials = testimonials.filter(status=status)
    if search:
        testimonials = testimonials.filter(Q(client_name__icontains=search) | Q(email__icontains=search) | Q(company_role__icontains=search) | Q(message__icontains=search))
    if rating in {str(number) for number in range(1, 6)}:
        testimonials = testimonials.filter(rating=int(rating))

    approved = space.testimonials.filter(status=Testimonial.Status.APPROVED)
    metrics = approved.aggregate(total=Count("id"), average=Avg("rating"))
    distribution = {number: approved.filter(rating=number).count() for number in range(5, 0, -1)}
    status_counts = {"all": space.testimonials.count()}
    status_counts.update({key: space.testimonials.filter(status=key).count() for key, _ in Testimonial.Status.choices})
    host = request.get_host()
    scheme = "https" if request.is_secure() else "http"
    embed_url = f"{scheme}://{host}{reverse('embed_widget', args=[space.slug])}"

    return render(request, "collector/dashboard.html", {
        "spaces": spaces,
        "space": space,
        "testimonials": testimonials,
        "status": status,
        "search": search,
        "rating": rating,
        "metrics": metrics,
        "distribution": distribution,
        "status_counts": status_counts,
        "embed_url": embed_url,
    })


@login_required
def space_create(request):
    form = SpaceForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        space = form.save(commit=False)
        space.owner = request.user
        space.save()
        messages.success(request, f"{space.name} is ready to collect testimonials.")
        return redirect(f"{reverse('dashboard')}?space={space.slug}")
    return render(request, "collector/space_form.html", {"form": form, "title": "Create a new Space", "submit_label": "Create Space"})


@login_required
def space_edit(request, slug):
    space = get_object_or_404(Space, slug=slug, owner=request.user)
    form = SpaceForm(request.POST or None, request.FILES or None, instance=space)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Space settings saved.")
        return redirect(f"{reverse('dashboard')}?space={space.slug}")
    return render(request, "collector/space_form.html", {"form": form, "space": space, "title": f"Edit {space.name}", "submit_label": "Save changes"})


@login_required
@require_POST
def testimonial_action(request, pk, action):
    testimonial = get_object_or_404(Testimonial, pk=pk, space__owner=request.user)
    if action == "approve":
        testimonial.status = Testimonial.Status.APPROVED
        notice = "Testimonial approved and added to the Wall of Love."
    elif action == "reject":
        testimonial.status = Testimonial.Status.REJECTED
        notice = "Testimonial rejected."
    elif action == "archive":
        testimonial.status = Testimonial.Status.ARCHIVED
        notice = "Testimonial archived."
    elif action == "feature":
        testimonial.is_featured = not testimonial.is_featured
        notice = "Featured status updated."
    elif action == "like":
        testimonial.is_liked = not testimonial.is_liked
        notice = "Liked status updated."
    else:
        raise Http404("Unknown testimonial action")
    testimonial.save()
    messages.success(request, notice)
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect(f"{reverse('dashboard')}?space={testimonial.space.slug}")


def collect_testimonial(request, slug):
    space = get_object_or_404(Space, slug=slug)
    form = TestimonialForm(request.POST or None, request.FILES or None, space=space)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("collect_thanks", slug=space.slug)
    return render(request, "collector/collect_form.html", {"space": space, "form": form})


def collect_thanks(request, slug):
    space = get_object_or_404(Space, slug=slug)
    return render(request, "collector/thank_you.html", {"space": space})


def wall(request, slug):
    space = get_object_or_404(Space, slug=slug)
    testimonials = space.testimonials.filter(status=Testimonial.Status.APPROVED)
    stats = testimonials.aggregate(total=Count("id"), average=Avg("rating"))
    return render(request, "collector/wall.html", {"space": space, "testimonials": testimonials, "stats": stats})


def embed_widget(request, slug):
    space = get_object_or_404(Space, slug=slug)
    testimonials = space.testimonials.filter(status=Testimonial.Status.APPROVED)[:6]
    return render(request, "collector/embed_widget.html", {"space": space, "testimonials": testimonials})


class CookieTokenObtainPairView(TokenObtainPairView):
    """Return a short-lived access token and keep the refresh token out of JavaScript."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", None)
        if refresh:
            response.set_cookie(
                "proofly_refresh", refresh, max_age=7 * 24 * 60 * 60,
                httponly=True, secure=settings.COOKIE_SECURE, samesite="Lax",
            )
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.data.get("refresh") or request.COOKIES.get("proofly_refresh")
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", None)
        if refresh:
            response.set_cookie(
                "proofly_refresh", refresh, max_age=7 * 24 * 60 * 60,
                httponly=True, secure=settings.COOKIE_SECURE, samesite="Lax",
            )
        return response
