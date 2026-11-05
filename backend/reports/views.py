from datetime import timedelta
from django.db.models import Count, Avg
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from tickets.models import Ticket
from feedback.models import TicketFeedback


class AdminDashboardReportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.localdate()
        start_date = today - timedelta(days=29)
        tickets = Ticket.objects.all()
        status_counts = {row['status']: row['total'] for row in tickets.values('status').annotate(total=Count('id'))}
        priority_counts = {row['priority']: row['total'] for row in tickets.values('priority').annotate(total=Count('id'))}
        category_counts = list(tickets.values('category__name', 'category__code').annotate(total=Count('id')).order_by('-total'))
        daily_counts = list(tickets.filter(created_at__date__gte=start_date).values('created_at__date').annotate(total=Count('id')).order_by('created_at__date'))
        feedback = TicketFeedback.objects.aggregate(average_rating=Avg('rating'), total_feedback=Count('id'))
        return Response({
            'total_tickets': tickets.count(),
            'status_counts': status_counts,
            'priority_counts': priority_counts,
            'category_counts': category_counts,
            'daily_tickets_last_30_days': daily_counts,
            'feedback': feedback,
        })
