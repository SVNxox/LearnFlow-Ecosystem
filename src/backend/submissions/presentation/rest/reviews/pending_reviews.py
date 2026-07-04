"""
Pending Reviews API View

GET /api/v1/reviews/pending/ - Get mentor work queue
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.submissions.application.queries import GetPendingReviewsQuery
from src.backend.submissions.presentation.rest.reviews.serializers import (
    PendingReviewSerializer
)


class PendingReviewsView(APIView):
    """
    Get submissions waiting for review (mentor work queue).

    GET /api/v1/reviews/pending/
    Query params:
    - limit (optional, default 50): max number of results

    Permissions: IsAuthenticated (Mentor)
    """
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        limit = int(request.query_params.get('limit', 50))

        
        limit = min(max(limit, 1), 100)

        pending_reviews = GetPendingReviewsQuery.execute(
            mentor_id=request.user.id,
            limit=limit
        )

        serializer = PendingReviewSerializer(pending_reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
