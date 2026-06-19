from .models import ClubJoinRequest, User


def manager_pending_requests(request):
    if not request.user.is_authenticated or request.user.role != User.Role.CLUB_MANAGER:
        return {"manager_pending_requests_count": 0}

    managed_club = getattr(request.user, "managed_club", None)
    if not managed_club:
        return {"manager_pending_requests_count": 0}

    count = ClubJoinRequest.objects.filter(
        club=managed_club, status=ClubJoinRequest.Status.PENDING
    ).count()
    return {"manager_pending_requests_count": count}
