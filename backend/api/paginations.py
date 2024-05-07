from rest_framework import pagination


class CustomPagePagination(pagination.PageNumberPagination):

    page_size_query_param = 'limit'
