from django.urls import path

from .views import (
    UserLoginView,
    admin_dashboard,
    admin_events,
    approve_join_request,
    approve_club_request,
    approve_event_request,
    club_detail,
    club_events,
    club_list,
    create_club_request,
    create_event_request,
    create_student,
    dashboard,
    delete_managed_club,
    delete_student,
    leave_club,
    managed_club_members,
    manager_dashboard,
    profile_view,
    register_view,
    reject_club_request,
    reject_event_request,
    reject_join_request,
    register_event,
    unregister_event,
    remove_member,
    request_join_club,
    student_dashboard,
    update_student,
    user_logout,
    delete_event,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", register_view, name="register"),
    path("profile/", profile_view, name="profile"),
    path("logout/", user_logout, name="logout"),

    # Student
    path("student/", student_dashboard, name="student_dashboard"),

    # Manager
    path("manager/", manager_dashboard, name="manager_dashboard"),
    path("manager/members/", managed_club_members, name="managed_club_members"),
    path("manager/members/<int:membership_id>/remove/", remove_member, name="remove_member"),
    path("manager/club/delete/", delete_managed_club, name="delete_managed_club"),
    path("manager/join-requests/<int:request_id>/approve/", approve_join_request, name="approve_join_request"),
    path("manager/join-requests/<int:request_id>/reject/", reject_join_request, name="reject_join_request"),

    # Admin
    path("administration/", admin_dashboard, name="admin_dashboard"),
    path("administration/events/", admin_events, name="admin_events"),
    path("administration/club-requests/<int:request_id>/approve/", approve_club_request, name="approve_club_request"),
    path("administration/club-requests/<int:request_id>/reject/", reject_club_request, name="reject_club_request"),
    path("administration/event-requests/<int:request_id>/approve/", approve_event_request, name="approve_event_request"),
    path("administration/event-requests/<int:request_id>/reject/", reject_event_request, name="reject_event_request"),
    path("administration/students/create/", create_student, name="create_student"),
    path("administration/students/<int:student_id>/update/", update_student, name="update_student"),
    path("administration/students/<int:user_id>/delete/", delete_student, name="delete_student"),

    # Clubs
    path("clubs/", club_list, name="club_list"),
    path("clubs/<int:club_id>/", club_detail, name="club_detail"),
    path("clubs/request-join/", request_join_club, name="request_join_club"),
    path("clubs/<int:club_id>/leave/", leave_club, name="leave_club"),
    path("clubs/request-create/", create_club_request, name="create_club_request"),

    # Events
    path("events/", club_events, name="club_events"),
    path("events/request-create/", create_event_request, name="create_event_request"),
    path("events/<int:event_id>/register/", register_event, name="register_event"),
    path("events/<int:event_id>/unregister/", unregister_event, name="unregister_event"),
    path("events/<int:event_id>/delete/", delete_event, name="delete_event"),
]
