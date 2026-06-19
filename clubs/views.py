from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ClubCreationRequestForm,
    ClubJoinRequestForm,
    EventRequestForm,
    LoginForm,
    UserCreationByAdminForm,
    UserUpdateByAdminForm,
    UserRegistrationForm,
    UserProfileForm,
)
from .models import (
    Club,
    ClubCreationRequest,
    ClubJoinRequest,
    ClubMembership,
    Event,
    EventRegistration,
    EventRequest,
    User,
)


def _require_role(request, allowed_roles):
    if request.user.role not in allowed_roles:
        messages.error(request, "Acces refuse pour votre role.")
        return False
    return True


class UserLoginView(LoginView):
    template_name = "clubs/login.html"
    authentication_form = LoginForm


@login_required
def dashboard(request):
    role = request.user.role
    if role == User.Role.ADMINISTRATION:
        return redirect("admin_dashboard")
    if role == User.Role.CLUB_MANAGER:
        return redirect("manager_dashboard")
    return redirect("student_dashboard")


@login_required
def student_dashboard(request):
    if not _require_role(request, [User.Role.STUDENT]):
        return redirect("dashboard")
    memberships = ClubMembership.objects.filter(user=request.user).select_related("club")
    return render(request, "clubs/student_dashboard.html", {"memberships": memberships})


@login_required
def manager_dashboard(request):
    if not _require_role(request, [User.Role.CLUB_MANAGER]):
        return redirect("dashboard")
    memberships = ClubMembership.objects.filter(user=request.user).select_related("club")
    managed_club = getattr(request.user, "managed_club", None)
    managed_events = Event.objects.filter(club=managed_club).order_by("-event_date") if managed_club else []
    pending_join_requests = (
        ClubJoinRequest.objects.filter(club=managed_club, status=ClubJoinRequest.Status.PENDING).select_related("user")
        if managed_club
        else []
    )
    return render(
        request,
        "clubs/manager_dashboard.html",
        {
            "memberships": memberships,
            "managed_club": managed_club,
            "managed_events": managed_events,
            "pending_join_requests": pending_join_requests,
        },
    )


@login_required
def admin_dashboard(request):
    if not _require_role(request, [User.Role.ADMINISTRATION]):
        return redirect("dashboard")

    context = {
        "students": User.objects.exclude(role=User.Role.ADMINISTRATION),
        "clubs_count": Club.objects.count(),
        "students_count": User.objects.count(),
        "club_requests": ClubCreationRequest.objects.filter(status=ClubCreationRequest.Status.PENDING),
        "event_requests": EventRequest.objects.filter(status=EventRequest.Status.PENDING),
        "pending_club_count": ClubCreationRequest.objects.filter(status=ClubCreationRequest.Status.PENDING).count(),
        "pending_event_count": EventRequest.objects.filter(status=EventRequest.Status.PENDING).count(),
    }
    return render(request, "clubs/admin_dashboard.html", context)


@login_required
def club_list(request):
    
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")
    
    clubs = Club.objects.prefetch_related("memberships").all()
    if query:
        clubs = clubs.filter(name__icontains=query)
    if category:
        clubs = clubs.filter(category=category)
        
    return render(request, "clubs/club_list.html", {"clubs": clubs, "query": query, "category": category})


@login_required
def request_join_club(request):
    if not _require_role(request, [User.Role.STUDENT, User.Role.CLUB_MANAGER]):
        return redirect("dashboard")
    if request.method == "POST":
        form = ClubJoinRequestForm(request.POST)
        if form.is_valid():
            club = form.cleaned_data["club"]
            managed_club = getattr(request.user, "managed_club", None)
            if request.user.role == User.Role.CLUB_MANAGER and managed_club and club == managed_club:
                messages.error(request, "Vous ne pouvez pas demander de rejoindre votre propre club.")
            elif ClubMembership.objects.filter(user=request.user, club=club).exists():
                messages.error(request, "Vous etes deja membre de ce club.")
            elif ClubMembership.objects.filter(user=request.user).count() >= request.user.max_joinable_clubs():
                messages.error(request, "Vous avez atteint votre limite de clubs.")
            elif ClubJoinRequest.objects.filter(
                user=request.user, club=club, status=ClubJoinRequest.Status.PENDING
            ).exists():
                messages.info(request, "Vous avez deja une demande en attente pour ce club.")
            else:
                ClubJoinRequest.objects.get_or_create(user=request.user, club=club)
                messages.success(request, "Demande envoyee.")
            return redirect("club_list")
    else:
        form = ClubJoinRequestForm()
    return render(request, "clubs/request_join_club.html", {"form": form})


@login_required
def leave_club(request, club_id):
    if not _require_role(request, [User.Role.STUDENT, User.Role.CLUB_MANAGER]):
        return redirect("dashboard")
    membership = get_object_or_404(ClubMembership, user=request.user, club_id=club_id)
    membership.delete()
    messages.success(request, "Vous avez quitte le club.")
    return redirect("dashboard")


@login_required
def create_club_request(request):
    if request.user.role not in [User.Role.STUDENT, User.Role.CLUB_MANAGER]:
        messages.error(request, "Action non autorisee.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ClubCreationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            club_request = form.save(commit=False)
            club_request.student = request.user
            club_request.save()
            messages.success(request, "Demande de creation de club envoyee.")
            return redirect("dashboard")
    else:
        form = ClubCreationRequestForm()
    return render(request, "clubs/create_club_request.html", {"form": form})


@login_required
def create_event_request(request):
    if request.user.role != User.Role.CLUB_MANAGER:
        messages.error(request, "Action reservee au responsable.")
        return redirect("dashboard")

    managed_club = getattr(request.user, "managed_club", None)
    if not managed_club:
        messages.error(request, "Aucun club gere.")
        return redirect("dashboard")

    if request.method == "POST":
        form = EventRequestForm(request.POST)
        if form.is_valid():
            event_request = form.save(commit=False)
            event_request.club = managed_club
            event_request.requested_by = request.user
            event_request.save()
            messages.success(request, "Demande d'evenement envoyee.")
            return redirect("dashboard")
    else:
        form = EventRequestForm()
    return render(request, "clubs/create_event_request.html", {"form": form})


@login_required
def club_events(request):
    # Show all events to all authenticated users
    events = Event.objects.select_related("club").order_by("-event_date")
    # Get IDs of events the user is registered for
    registered_event_ids = list(
        EventRegistration.objects.filter(user=request.user).values_list("event_id", flat=True)
    )
    return render(request, "clubs/club_events.html", {"events": events, "registered_event_ids": registered_event_ids})


@login_required
def admin_events(request):
    if not _require_role(request, [User.Role.ADMINISTRATION]):
        return redirect("dashboard")
    events = Event.objects.select_related("club").order_by("-event_date")
    return render(request, "clubs/club_events.html", {"events": events, "registered_event_ids": []})


@login_required
def register_event(request, event_id):
    if not _require_role(request, [User.Role.STUDENT, User.Role.CLUB_MANAGER]):
        return redirect("dashboard")
    event = get_object_or_404(Event, pk=event_id)
    try:
        EventRegistration.objects.create(user=request.user, event=event)
        messages.success(request, "Inscription confirmée !")
    except IntegrityError:
        messages.info(request, "Vous êtes déjà inscrit à cet événement.")
    return redirect("club_events")


@login_required
def unregister_event(request, event_id):
    if not _require_role(request, [User.Role.STUDENT, User.Role.CLUB_MANAGER]):
        return redirect("dashboard")
    event = get_object_or_404(Event, pk=event_id)
    deleted, _ = EventRegistration.objects.filter(user=request.user, event=event).delete()
    if deleted:
        messages.success(request, f"Désinscription de '{event.title}' confirmée.")
    else:
        messages.info(request, "Vous n'étiez pas inscrit à cet événement.")
    return redirect("club_events")



@login_required
def managed_club_members(request):
    if request.user.role != User.Role.CLUB_MANAGER:
        messages.error(request, "Acces refuse.")
        return redirect("dashboard")

    managed_club = getattr(request.user, "managed_club", None)
    memberships = ClubMembership.objects.filter(club=managed_club).select_related("user") if managed_club else []
    return render(request, "clubs/managed_club_members.html", {"memberships": memberships, "club": managed_club})


@login_required
def remove_member(request, membership_id):
    if request.user.role != User.Role.CLUB_MANAGER:
        messages.error(request, "Action non autorisee.")
        return redirect("dashboard")

    managed_club = getattr(request.user, "managed_club", None)
    membership = get_object_or_404(ClubMembership, pk=membership_id, club=managed_club)
    membership.delete()
    messages.success(request, "Membre supprime.")
    return redirect("managed_club_members")


@login_required
def delete_managed_club(request):
    if request.user.role != User.Role.CLUB_MANAGER:
        messages.error(request, "Action non autorisee.")
        return redirect("dashboard")
    managed_club = getattr(request.user, "managed_club", None)
    if managed_club:
        managed_club.delete()
        messages.success(request, "Club supprime.")
    return redirect("dashboard")


@login_required
def approve_club_request(request, request_id):
    if request.user.role != User.Role.ADMINISTRATION:
        messages.error(request, "Acces refuse.")
        return redirect("dashboard")

    club_request = get_object_or_404(ClubCreationRequest, pk=request_id)
    if club_request.status == ClubCreationRequest.Status.PENDING:
        manager = club_request.student
        manager.role = User.Role.CLUB_MANAGER
        manager.save()
        Club.objects.create(
            name=club_request.club_name,
            description=club_request.description,
            logo=club_request.logo,
            manager=manager,
        )
        club_request.status = ClubCreationRequest.Status.APPROVED
        club_request.save()
        messages.success(request, "Demande de club acceptee.")
    return redirect("admin_dashboard")


@login_required
def reject_club_request(request, request_id):
    if request.user.role != User.Role.ADMINISTRATION:
        messages.error(request, "Acces refuse.")
        return redirect("dashboard")
    club_request = get_object_or_404(ClubCreationRequest, pk=request_id)
    club_request.status = ClubCreationRequest.Status.REJECTED
    club_request.save()
    messages.info(request, "Demande de club rejetee.")
    return redirect("admin_dashboard")


@login_required
def approve_event_request(request, request_id):
    if request.user.role != User.Role.ADMINISTRATION:
        messages.error(request, "Acces refuse.")
        return redirect("dashboard")
    event_request = get_object_or_404(EventRequest, pk=request_id)
    if event_request.status == EventRequest.Status.PENDING:
        Event.objects.create(
            club=event_request.club,
            title=event_request.title,
            description=event_request.description,
            event_date=event_request.event_date,
            event_time=event_request.event_time,
            location=event_request.location,
        )
        event_request.status = EventRequest.Status.APPROVED
        event_request.save()
        messages.success(request, "Demande d'evenement acceptee.")
    return redirect("admin_dashboard")


@login_required
def reject_event_request(request, request_id):
    if request.user.role != User.Role.ADMINISTRATION:
        messages.error(request, "Acces refuse.")
        return redirect("dashboard")
    event_request = get_object_or_404(EventRequest, pk=request_id)
    event_request.status = EventRequest.Status.REJECTED
    event_request.save()
    messages.info(request, "Demande d'evenement rejetee.")
    return redirect("admin_dashboard")


@login_required
def approve_join_request(request, request_id):
    if request.user.role != User.Role.CLUB_MANAGER:
        return redirect("dashboard")
    managed_club = getattr(request.user, "managed_club", None)
    if not managed_club:
        return redirect("dashboard")
    join_request = get_object_or_404(ClubJoinRequest, pk=request_id, club=managed_club)
    if join_request.status == ClubJoinRequest.Status.PENDING:
        try:
            ClubMembership.objects.create(user=join_request.user, club=join_request.club)
            join_request.status = ClubJoinRequest.Status.APPROVED
            join_request.save()
            messages.success(request, "Demande de rejoindre club acceptee.")
        except Exception:
            messages.error(request, "Impossible d'accepter cette demande.")
    return redirect("manager_dashboard")


@login_required
def reject_join_request(request, request_id):
    if request.user.role != User.Role.CLUB_MANAGER:
        return redirect("dashboard")
    managed_club = getattr(request.user, "managed_club", None)
    if not managed_club:
        return redirect("dashboard")
    join_request = get_object_or_404(ClubJoinRequest, pk=request_id, club=managed_club)
    join_request.status = ClubJoinRequest.Status.REJECTED
    join_request.save()
    messages.info(request, "Demande de rejoindre club rejetee.")
    return redirect("manager_dashboard")


@login_required
def create_student(request):
    if request.user.role != User.Role.ADMINISTRATION:
        return redirect("dashboard")
    if request.method == "POST":
        form = UserCreationByAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Etudiant ajoute.")
            return redirect("admin_dashboard")
    else:
        form = UserCreationByAdminForm()
    return render(request, "clubs/create_student.html", {"form": form})


@login_required
def update_student(request, student_id):
    if not _require_role(request, [User.Role.ADMINISTRATION]):
        return redirect("dashboard")
    student = get_object_or_404(User, id=student_id)
    if request.method == "POST":
        form = UserUpdateByAdminForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur mis a jour avec succes.")
            return redirect("admin_dashboard")
    else:
        form = UserUpdateByAdminForm(instance=student)
    return render(request, "clubs/update_student.html", {"form": form, "student": student})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "clubs/register.html", {"form": form})


@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "clubs/profile.html", {"form": form})


@login_required
def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    events = club.events.all().order_by('-event_date')
    members = ClubMembership.objects.filter(club=club)
    return render(request, "clubs/club_detail.html", {"club": club, "events": events, "members": members})


@login_required
def delete_student(request, user_id):
    if request.user.role != User.Role.ADMINISTRATION:
        return redirect("dashboard")
    student = get_object_or_404(User, pk=user_id)
    if student != request.user:
        student.delete()
        messages.success(request, "Etudiant supprime.")
    return redirect("admin_dashboard")


@login_required
def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def delete_event(request, event_id):
    if request.user.role != User.Role.ADMINISTRATION:
        messages.error(request, "Action réservée à l'administration.")
        return redirect("club_events")
    event = get_object_or_404(Event, id=event_id)
    title = event.title
    event.delete()
    messages.success(request, f"L'événement '{title}' a été supprimé.")
    return redirect("club_events")
