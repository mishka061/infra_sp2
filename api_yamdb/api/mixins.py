from rest_framework import mixins, viewsets


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """
    Класс вьюсета для получения списка объектов, создания нового и удаления.
    """
    pass
