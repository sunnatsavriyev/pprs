from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 50  # default
    page_size_query_param = "limit"
    page_query_param = "page"

    def add_extra_params(self, url, request):
        """Frontend yuborgan query paramlarni next/prev urlga qo'shib beradi"""
        if not url:
            return None

        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # frontenddan kelgan barcha querylarni olish
        for key, value in request.query_params.items():
            if key not in query_params:  # agar qo'shilmagan bo'lsa
                query_params[key] = [value]

        new_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed_url._replace(query=new_query))

    def get_paginated_response(self, data):
        request = self.request

        next_url = self.add_extra_params(self.get_next_link(), request)
        prev_url = self.add_extra_params(self.get_previous_link(), request)

        return Response({
            "count": self.page.paginator.count,
            "next": next_url,
            "previous": prev_url,
            "results": data,
        })
