from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import ClubCreationRequest, ClubJoinRequest, EventRequest, User


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email ou nom d'utilisateur")


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Doit se terminer par @emsi.ma")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    filiere = forms.CharField(max_length=100, required=True, label="Filière")
    role = forms.ChoiceField(choices=[(User.Role.STUDENT, "Étudiant"), (User.Role.CLUB_MANAGER, "Responsable de club")], required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "filiere", "role")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@emsi.ma"):
            raise ValidationError("L'email doit se terminer par @emsi.ma")
        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "filiere"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@emsi.ma"):
            raise ValidationError("L'email doit se terminer par @emsi.ma")
        return email


class ClubJoinRequestForm(forms.ModelForm):
    class Meta:
        model = ClubJoinRequest
        fields = ["club"]


class ClubCreationRequestForm(forms.ModelForm):
    class Meta:
        model = ClubCreationRequest
        fields = ["club_name", "description", "logo"]


class EventRequestForm(forms.ModelForm):
    class Meta:
        model = EventRequest
        fields = ["title", "description", "event_date", "event_time", "location"]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "event_time": forms.TimeInput(attrs={"type": "time"}),
        }


class UserCreationByAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "filiere", "role", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = [
            (User.Role.STUDENT, "Etudiant"),
            (User.Role.CLUB_MANAGER, "Responsable de club"),
            (User.Role.ADMINISTRATION, "Administration"),
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserUpdateByAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "filiere", "role", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = [
            (User.Role.STUDENT, "Etudiant"),
            (User.Role.CLUB_MANAGER, "Responsable de club"),
            (User.Role.ADMINISTRATION, "Administration"),
        ]
