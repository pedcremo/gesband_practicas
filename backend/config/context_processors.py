from django.conf import settings

def gesband_version(request):
    return {"GESBAND_VERSION": settings.GESBAND_VERSION}
