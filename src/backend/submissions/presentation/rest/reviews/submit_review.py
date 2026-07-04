"""
Submit Review API View

POST /api/v1/reviews/ - Mentor submits review
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.submissions.application.commands import (
    RequestChangesCommand,
    RequestChangesHandler,
    ApproveSubmissionCommand,
    ApproveSubmissionHandler,
    RejectSubmissionCommand,
    RejectSubmissionHandler
)
from src.backend.submissions.presentation.rest.reviews.serializers import (
    SubmitReviewSerializer,
    ReviewResponseSerializer
)


class SubmitReviewView(APIView):
    """
    Submit review for submission.

    POST /api/v1/reviews/

    Permissions: IsAuthenticated (Mentor)
    """
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        serializer = SubmitReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review_status = serializer.validated_data['status']

        try:
            
            if review_status == 'changes_requested':
                command = RequestChangesCommand(
                    submission_id=serializer.validated_data['submission_id'],
                    revision_id=serializer.validated_data['revision_id'],
                    mentor_id=request.user.id,
                    score=serializer.validated_data['score'],
                    feedback=serializer.validated_data['feedback']
                )
                review = RequestChangesHandler.handle(command)

            elif review_status == 'approved':
                command = ApproveSubmissionCommand(
                    submission_id=serializer.validated_data['submission_id'],
                    revision_id=serializer.validated_data['revision_id'],
                    mentor_id=request.user.id,
                    score=serializer.validated_data['score'],
                    feedback=serializer.validated_data['feedback']
                )
                review = ApproveSubmissionHandler.handle(command)

            elif review_status == 'rejected':
                command = RejectSubmissionCommand(
                    submission_id=serializer.validated_data['submission_id'],
                    revision_id=serializer.validated_data['revision_id'],
                    mentor_id=request.user.id,
                    score=serializer.validated_data['score'],
                    feedback=serializer.validated_data['feedback']
                )
                review = RejectSubmissionHandler.handle(command)

            else:
                return Response(
                    {"error": f"Invalid status: {review_status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            response_data = {
                'id': review.id,
                'submission_id': review.submission_id,
                'revision_id': review.revision_id,
                'mentor_id': review.mentor_id,
                'score': review.score,
                'max_score': review.max_score,
                'feedback': review.feedback,
                'status': review.status,
                'reviewed_at': review.reviewed_at.isoformat()
            }

            response_serializer = ReviewResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
