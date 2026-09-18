from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Space, Testimonial


class CollectionFlowTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user("owner", "owner@example.com", "password123")
        self.space = Space.objects.create(owner=self.owner, name="Acme Studio", slug="acme-studio")

    def test_public_form_creates_pending_testimonial(self):
        response = self.client.post(reverse("collect_testimonial", args=[self.space.slug]), {
            "client_name": "Maya Chen",
            "email": "maya@example.com",
            "company_role": "Founder",
            "rating": "5",
            "message": "The team made every step feel easy.",
        })
        self.assertRedirects(response, reverse("collect_thanks", args=[self.space.slug]))
        testimonial = Testimonial.objects.get()
        self.assertEqual(testimonial.status, Testimonial.Status.PENDING)
        self.assertEqual(testimonial.rating, 5)

    def test_wall_only_shows_approved_testimonials(self):
        Testimonial.objects.create(space=self.space, client_name="Approved", email="a@example.com", rating=5, message="Wonderful", status=Testimonial.Status.APPROVED)
        Testimonial.objects.create(space=self.space, client_name="Pending", email="p@example.com", rating=4, message="Still private")
        response = self.client.get(reverse("wall", args=[self.space.slug]))
        self.assertContains(response, "Approved")
        self.assertNotContains(response, "Pending")

    def test_owner_dashboard_renders_for_a_new_account(self):
        self.client.login(username="owner", password="password123")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Testimonials")
        self.assertContains(response, "Get embed code")

    def test_token_refresh_uses_the_http_only_cookie(self):
        response = self.client.post(reverse("token_obtain_pair"), {
            "username": "owner", "password": "password123",
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("proofly_refresh", response.cookies)
        refresh_response = self.client.post(reverse("token_refresh"), {}, content_type="application/json")
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.json())
