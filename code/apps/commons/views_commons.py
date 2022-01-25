from django.shortcuts import render
from config.settings.config_common import \
    LOGTAIL_SOURCE_TOKEN
import logging
logger = logging.getLogger(__name__)

class CommonErrorPageViews:
    
    def error_404(request, exception):
        logger.error("[404] " + str(exception))
        data = {}
        data["status"] = "404"
        data["message"] = "The page you are looking for does not exist."
        return render(request, 'online-store/404.html', status=404, context=data)

    def error_500(request):
        logger.error("[500] ")
        data = {}
        data["status"] = "500"
        data["message"] = "Internal Server Error"
        return render(request, 'online-store/error.html', status=500, context=data)

    def error_403(request, exception):
        logger.error("[403] " + str(exception))
        data = {}
        data["status"] = "403"
        data["message"] = "You do not have permission to access this page."
        return render(request, 'online-store/error.html', status=403, context=data)

    def error_400(request, exception):
        logger.error("[400] " + str(exception))
        data = {}
        data["status"] = "400"
        data["message"] = "Bad Request"
        return render(request, 'online-store/error.html', status=400, context=data)

class CommonPageViews:
    def store_page(request, page):
        if request.method == "GET":
            return render(request, "online-store/" + page + ".html")

    def admin_page(request, page):
        if request.method == "GET":
            return render(request, "admin-portal/" + page, {})
