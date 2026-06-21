from django.conf import settings

def cdn_processor(request):
    """
    Context processor to inject CDN_URL into all templates
    for rendering images/media from an external CDN when deployed.
    """
    return {
        'CDN_URL': getattr(settings, 'CDN_URL', '')
    }
