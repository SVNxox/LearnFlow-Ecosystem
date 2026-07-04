"""
Student Assessment Views — для прохождения квизов студентами.
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from src.backend.assessment.domain.models import (
    ModuleAssessment, AssessmentItem, AssessmentOption,
    AssessmentAttempt, AssessmentResponse
)

logger = logging.getLogger(__name__)


class StudentAssessmentListView(APIView):
    """GET /api/v1/assessment/student/assessments/ — список доступных квизов."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = request.user

        
        assessments = ModuleAssessment.objects.filter(is_published=True)

        data = []
        for assessment in assessments:
            
            attempts_count = AssessmentAttempt.objects.filter(
                assessment=assessment,
                user_id=user.id
            ).count()

            data.append({
                "id": str(assessment.id),
                "title": assessment.title,
                "instructions": assessment.instructions,
                "max_attempts": assessment.max_attempts,
                "time_limit_minutes": assessment.time_limit_minutes,
                "attempts_count": attempts_count,
                "can_attempt": attempts_count < assessment.max_attempts,
                "items_count": assessment.items.count(),
            })

        return Response(data, status=status.HTTP_200_OK)


class StudentAssessmentDetailView(APIView):
    """GET /api/v1/assessment/student/assessments/<id>/ — детали квиза."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, assessment_id: str) -> Response:
        try:
            assessment = ModuleAssessment.objects.get(id=assessment_id, is_published=True)
        except ModuleAssessment.DoesNotExist:
            return Response({"detail": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

        items = assessment.items.all().order_by('order')
        items_data = []

        for item in items:
            item_data = {
                "id": str(item.id),
                "type": item.type,
                "title": item.title,
                "description": item.description,
                "max_points": str(item.max_points),
                "order": item.order,
            }

            
            if item.type == 'multiple_choice':
                options = item.options.all().order_by('order')
                item_data["options"] = [
                    {
                        "id": str(opt.id),
                        "text": opt.text,
                        "order": opt.order,
                    }
                    for opt in options
                ]

            
            if item.type == 'coding':
                item_data["starter_code"] = item.starter_code
                item_data["coding_language"] = item.coding_language

            items_data.append(item_data)

        return Response({
            "id": str(assessment.id),
            "title": assessment.title,
            "instructions": assessment.instructions,
            "time_limit_minutes": assessment.time_limit_minutes,
            "items": items_data,
        }, status=status.HTTP_200_OK)


class StartAssessmentAttemptView(APIView):
    """POST /api/v1/assessment/student/assessments/<id>/start/ — начать попытку."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, assessment_id: str) -> Response:
        user = request.user

        try:
            assessment = ModuleAssessment.objects.get(id=assessment_id, is_published=True)
        except ModuleAssessment.DoesNotExist:
            return Response({"detail": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

        
        attempts_count = AssessmentAttempt.objects.filter(
            assessment=assessment,
            user_id=user.id
        ).count()

        if attempts_count >= assessment.max_attempts:
            return Response(
                {"detail": "Max attempts reached"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        attempt = AssessmentAttempt.objects.create(
            assessment=assessment,
            user_id=user.id,
            attempt_number=attempts_count + 1,
            grading_status='pending',
            started_at=timezone.now(),
            max_score=sum(item.max_points for item in assessment.items.all()),
        )

        logger.info(f"Assessment attempt started: {attempt.id} by user {user.id}")

        return Response({
            "attempt_id": str(attempt.id),
            "attempt_number": attempt.attempt_number,
            "max_score": str(attempt.max_score),
            "started_at": attempt.started_at.isoformat(),
        }, status=status.HTTP_201_CREATED)


class SubmitAssessmentResponseView(APIView):
    """POST /api/v1/assessment/student/attempts/<id>/responses/ — отправить ответ."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, attempt_id: str) -> Response:
        user = request.user
        data = request.data

        try:
            attempt = AssessmentAttempt.objects.get(id=attempt_id, user_id=user.id)
        except AssessmentAttempt.DoesNotExist:
            return Response({"detail": "Attempt not found"}, status=status.HTTP_404_NOT_FOUND)

        item_id = data.get('item_id')
        if not item_id:
            return Response({"detail": "item_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = AssessmentItem.objects.get(id=item_id, assessment=attempt.assessment)
        except AssessmentItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        
        response, created = AssessmentResponse.objects.get_or_create(
            attempt=attempt,
            item=item,
            defaults={
                'selected_option_ids': data.get('selected_option_ids', []),
                'text_response': data.get('text_response', ''),
                'submitted_code': data.get('submitted_code', ''),
                'coding_language': data.get('coding_language', 'python'),
            }
        )

        if not created:
            response.selected_option_ids = data.get('selected_option_ids', response.selected_option_ids)
            response.text_response = data.get('text_response', response.text_response)
            response.submitted_code = data.get('submitted_code', response.submitted_code)
            response.save()

        return Response({
            "response_id": str(response.id),
            "item_id": str(item.id),
            "created": created,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SubmitAssessmentAttemptView(APIView):
    """POST /api/v1/assessment/student/attempts/<id>/submit/ — завершить попытку."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, attempt_id: str) -> Response:
        user = request.user

        try:
            attempt = AssessmentAttempt.objects.get(id=attempt_id, user_id=user.id)
        except AssessmentAttempt.DoesNotExist:
            return Response({"detail": "Attempt not found"}, status=status.HTTP_404_NOT_FOUND)

        
        total_score = 0
        responses = attempt.responses.all()

        for response in responses:
            item = response.item

            
            if item.type == 'multiple_choice':
                correct_options = item.options.filter(is_correct=True).values_list('id', flat=True)
                selected = set(response.selected_option_ids or [])
                correct = set(str(opt_id) for opt_id in correct_options)

                if selected == correct:
                    response.auto_points = item.max_points
                    response.is_correct = True
                else:
                    response.auto_points = 0
                    response.is_correct = False

                response.final_points = response.auto_points
                response.is_graded = True
                response.save()

                total_score += response.final_points

            
            elif not item.mentor_review_required:
                response.is_graded = True
                response.final_points = 0  
                response.save()

        
        attempt.submitted_at = timezone.now()
        attempt.final_score = total_score
        attempt.percentage = (total_score / attempt.max_score * 100) if attempt.max_score > 0 else 0
        attempt.passed = attempt.percentage >= attempt.assessment.passing_percentage

        
        all_graded = all(r.is_graded for r in responses)
        if all_graded:
            attempt.grading_status = 'completed'
            attempt.graded_at = timezone.now()
        else:
            attempt.grading_status = 'partial'

        attempt.save()

        logger.info(f"Assessment attempt submitted: {attempt.id}, score: {total_score}/{attempt.max_score}")

        return Response({
            "attempt_id": str(attempt.id),
            "final_score": str(attempt.final_score),
            "max_score": str(attempt.max_score),
            "percentage": str(attempt.percentage),
            "passed": attempt.passed,
            "grading_status": attempt.grading_status,
        }, status=status.HTTP_200_OK)