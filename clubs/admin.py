from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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

admin.site.register(User, UserAdmin)
admin.site.register(Club)
admin.site.register(ClubMembership)
admin.site.register(ClubJoinRequest)
admin.site.register(ClubCreationRequest)
admin.site.register(Event)
admin.site.register(EventRequest)
admin.site.register(EventRegistration)
