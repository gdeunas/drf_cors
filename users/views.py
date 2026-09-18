# users/views.py
from rest_framework import generics
from users.models import User
from users.serializers import UserProfileSerializer, UserSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Payment
from .serializers import PaymentSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated


from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer
from .services import create_stripe_product, create_stripe_price, create_stripe_session


class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Эндпоинт для просмотра и редактирования профиля пользователя.
    Принимает PUT и PATCH запросы для обновления по id.
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = ("paid_course", "paid_lesson", "payment_method")

    ordering_fields = ("payment_date",)


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class PaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Сохраняем платеж с привязкой к текущему авторизованному пользователю
        payment = serializer.save(user=self.request.user)

        # Получаем название курса и его стоимость
        course_name = payment.course.title
        amount = payment.amount

        # Интеграция со Stripe через сервисные функции
        product_id = create_stripe_product(course_name)
        price_id = create_stripe_price(amount, product_id)
        payment_link, session_id = create_stripe_session(price_id)

        # Обновляем объект платежа созданными данными
        payment.payment_link = payment_link
        payment.session_id = session_id
        payment.save()
