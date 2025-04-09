from django.contrib import admin
from .models import TrackedEntity, TrackingRequest
from django.utils.html import format_html

@admin.register(TrackedEntity)
class TrackedEntityAdmin(admin.ModelAdmin):
    list_display = ('identifier_type', 'identifier_value', 'entity_type', 'first_seen')
    list_filter = ('entity_type', 'identifier_type')
    search_fields = ('identifier_value',)
    readonly_fields = ('first_seen', 'last_updated')

@admin.register(TrackingRequest)
class TrackingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester', 'status', 'warrant_id', 'start_date', 'end_date')
    list_filter = ('status', 'requester__role')
    search_fields = ('warrant_id', 'legal_basis')
    raw_id_fields = ('requester', 'approved_by')
    filter_horizontal = ('entities',)
    readonly_fields = ('created_at',)
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(
            status='APPROVED',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f"{updated} requests approved")
    approve_requests.short_description = "Approve selected requests"
