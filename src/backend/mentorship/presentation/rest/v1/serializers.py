"""
Mentorship serializers
"""

from rest_framework import serializers
from src.backend.mentorship.domain.models import Attendance, OfflineSession, MentorGroup


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for attendance."""

    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            'id',
            'session_id',
            'student_id',
            'student_name',
            'status',
            'status_display',
            'marked_at',
            'notes',
        ]
        read_only_fields = fields


class MarkAttendanceSerializer(serializers.Serializer):
    """Serializer for marking attendance."""

    student_id = serializers.UUIDField(required=True)
    status = serializers.ChoiceField(
        choices=['present', 'absent', 'late', 'excused'],
        required=True
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )


class BulkMarkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk marking attendance."""

    attendances = serializers.ListField(
        child=MarkAttendanceSerializer(),
        min_length=1,
        max_length=100
    )


class SessionDetailSerializer(serializers.ModelSerializer):
    """Serializer for session detail."""

    group_name = serializers.CharField(
        source='group.name',
        read_only=True
    )

    mentor_name = serializers.CharField(
        source='group.mentor.get_full_name',
        read_only=True
    )

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    attendances = AttendanceSerializer(many=True, read_only=True)

    class Meta:
        model = OfflineSession
        fields = [
            'id',
            'group_id',
            'group_name',
            'mentor_name',
            'lesson_id',
            'module_id',
            'title',
            'description',
            'scheduled_start',
            'scheduled_end',
            'actual_start',
            'actual_end',
            'status',
            'status_display',
            'location',
            'meeting_url',
            'notes',
            'attendances',
        ]
        read_only_fields = fields


class SessionListSerializer(serializers.ModelSerializer):
    """Serializer for session list."""

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    attendances_count = serializers.SerializerMethodField()

    class Meta:
        model = OfflineSession
        fields = [
            'id',
            'title',
            'scheduled_start',
            'scheduled_end',
            'status',
            'status_display',
            'location',
            'attendances_count',
        ]
        read_only_fields = fields

    def get_attendances_count(self, obj):
        """Get count of marked attendances."""
        return obj.attendances.count() if hasattr(obj, 'attendances') else 0
