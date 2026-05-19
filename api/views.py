from rest_framework import viewsets
from .models import Product, Order, Master, Category
from .serializers import ProductSerializer, OrderSerializer, MasterSerializer, CategorySerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from rest_framework.parsers import MultiPartParser, FormParser

class DashboardAnalyticsView(APIView):
    def get(self, request):
        # 1. Umumiy buyurtmalar soni
        total_orders = Order.objects.count()
        # 2. Jami ustalar soni
        total_masters = Master.objects.count()
        # 3. Faol ustalar soni (is_active=True)
        active_masters = Master.objects.filter(is_active=True).count()
        # 4. Oylik buyurtmalar dinamikasi (Grafik uchun oylar bo'yicha guruhlash)
        # Bu qism buyurtmalarni oylarga bo'lib, nechtadanligini sanab beradi
        monthly_data = (
            Order.objects.annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        # Grafik uchun oylik ma'lumotni chiroyli formatga keltiramiz
        chart_data = {item['month']: item['count'] for item in monthly_data}
        return Response({
            "total_orders": total_orders,
            "total_masters": total_masters,
            "active_masters": active_masters,
            "monthly_dynamics": chart_data  # Masalan: {5: 12, 6: 25} (5-oyda 12ta, 6-oyda 25ta buyurtma)
        })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser) # Rasmni qabul qilish uchun


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    # Ustunlar orasida kartochkani sursa (drag and drop), statusini oson yangilash uchun custom API
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in [choice[0] for choice in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save()
            return Response({'status': 'Status muvaffaqiyatli yangilandi'})
        return Response({'error': 'Noto\'g\'ri status'}, status=400)

class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer