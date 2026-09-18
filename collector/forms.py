import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify

from .models import Space, Testimonial


class StyledFormMixin:
    """Apply the shared CSS hooks without tying forms to a UI library."""

    def apply_styles(self):
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"input {existing}".strip()


class SignUpForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Used only for signing in."
        self.apply_styles()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account already uses that email address.")
        return email


class SpaceForm(StyledFormMixin, forms.ModelForm):
    custom_questions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "What would you tell a friend about us?\nWhat result did you get?"}),
        help_text="One optional question per line.",
    )

    class Meta:
        model = Space
        fields = ("name", "slug", "logo", "prompt", "require_avatar", "enable_ratings")
        widgets = {
            "prompt": forms.Textarea(attrs={"rows": 3}),
            "slug": forms.TextInput(attrs={"placeholder": "acme-design"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial["custom_questions"] = "\n".join(self.instance.custom_questions or [])
        self.apply_styles()
        for name in ("require_avatar", "enable_ratings"):
            self.fields[name].widget.attrs["class"] = "switch-input"

    def clean_slug(self):
        slug = slugify(self.cleaned_data["slug"])
        if not slug:
            raise forms.ValidationError("Use letters, numbers, or hyphens for the URL.")
        clashes = Space.objects.filter(slug=slug).exclude(pk=self.instance.pk)
        if clashes.exists():
            raise forms.ValidationError("That collection URL is already in use.")
        return slug

    def clean_custom_questions(self):
        lines = [re.sub(r"\s+", " ", line).strip() for line in self.cleaned_data["custom_questions"].splitlines()]
        return list(dict.fromkeys(line for line in lines if line))[:5]

    def save(self, commit=True):
        space = super().save(commit=False)
        space.custom_questions = self.cleaned_data["custom_questions"]
        if commit:
            space.save()
        return space


class TestimonialForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ("client_name", "email", "company_role", "rating", "message", "avatar")
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
            "rating": forms.HiddenInput(),
            "avatar": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, space, **kwargs):
        self.space = space
        super().__init__(*args, **kwargs)
        self.fields["company_role"].required = False
        self.fields["company_role"].label = "Your role or company"
        self.fields["avatar"].required = space.require_avatar
        self.fields["rating"].required = space.enable_ratings
        self.fields["message"].label = space.prompt
        if not space.enable_ratings:
            self.fields.pop("rating")
        for index, question in enumerate(space.custom_questions or []):
            self.fields[f"answer_{index}"] = forms.CharField(label=question, required=False, widget=forms.Textarea(attrs={"rows": 3}))
        self.apply_styles()

    def save(self, commit=True):
        testimonial = super().save(commit=False)
        testimonial.space = self.space
        testimonial.answers = {
            question: self.cleaned_data.get(f"answer_{index}", "")
            for index, question in enumerate(self.space.custom_questions or [])
            if self.cleaned_data.get(f"answer_{index}", "")
        }
        if commit:
            testimonial.save()
        return testimonial
