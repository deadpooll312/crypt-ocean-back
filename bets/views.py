from django.shortcuts import render
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from user.permissions import IsAuthenticated
from .serializers import CoefficientSerializer
from .models import Coefficient
from bets.serializers import BetCreationSerializer, BetSerializer

# Create your views here.


class CoefficientListAPIView(generics.ListAPIView):

    serializer_class = CoefficientSerializer
    queryset = Coefficient.objects.all()

    permission_classes = (IsAuthenticated,)


@method_decorator(swagger_auto_schema(
    query_serializer=BetCreationSerializer(),
    responses={
        201: BetSerializer()
    },
    operation_description='Make bet'
), name='dispatch')
class MakeBetAPIView(generics.CreateAPIView):

    serializer_class = BetCreationSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(BetSerializer(instance=instance).data, status=status.HTTP_201_CREATED, headers=headers)
