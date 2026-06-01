from rest_framework import viewsets
from .models import Product, Order, Master, Category
from .serializers import ProductSerializer, OrderSerializer, MasterSerializer, CategorySerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from rest_framework.parsers import MultiPartParser, FormParser



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


from rest_framework import viewsets, filters  # filters import qilindi
from django_filters.rest_framework import DjangoFilterBackend  # requirements.txt'da bor edi
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser) # Rasmni qabul qilish uchun
    # Qidiruv va filter tizimini yoqamiz
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # 1. Nomi bo'yicha qidirish (search)
    search_fields = ['name']

    # 2. Narxi va kategoriyasi bo'yicha to'g'ridan-to'g'ri filter qilish
    filterset_fields = ['price', 'category']

    # Narxini arzon-qimmat qilib tartiblash (Ordering) uchun ham imkoniyat ochamiz
    ordering_fields = ['price']



# Mavjud OrderViewSet kodingizni mana bundoq yangilang:
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    # Kanban kartochkasini drag-and-drop qilganda statusini yangilash uchun
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        # Modellardagi STATUS_CHOICES'ga tekshiramiz
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]

        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            return Response({'status': f'Status {new_status} ga yangilandi'})
        return Response({'error': 'Noto\'g\'ri status yuborildi'}, status=400)


# Tizim Hisoboti oynasi uchun eng pastga yangi klass qo'shing:
class DashboardAnalyticsView(APIView):
    def get(self, request):
        total_orders = Order.objects.count()
        total_masters = Master.objects.count()
        active_masters = Master.objects.filter(is_active=True).count()

        # Oylik buyurtmalar soni (Grafik uchun)
        monthly_data = (
            Order.objects.annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # Grafik ma'lumotlarini formatlash (Masalan: {"May": 15, "June": 24})
        months_mapping = {
            1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
            5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
            9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
        }

        chart_data = {}
        for item in monthly_data:
            month_name = months_mapping.get(item['month'], f"{item['month']}-oy")
            chart_data[month_name] = item['count']

        return Response({
            "total_orders": total_orders,
            "total_masters": total_masters,
            "active_masters": active_masters,
            "monthly_dynamics": chart_data
        })

class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer