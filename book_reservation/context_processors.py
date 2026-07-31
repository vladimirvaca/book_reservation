'''
Template context available on every rendered page (wired in settings.TEMPLATES).
'''
from django.conf import settings


def release(_request):
    '''
    Expose the deployed release to every template, so the running version is
    identifiable from any page (tab title, footer, sidebar) without having to
    curl /healthz or inspect the container.

    `app_revision` is the short git SHA baked into the image at build time;
    it is empty for local runs, which is itself a useful signal.
    '''
    tag = f'v{settings.APP_VERSION}'
    return {
        'app_version': settings.APP_VERSION,
        'app_release': tag,
        'app_revision': settings.APP_REVISION,
        'app_release_url': f'{settings.APP_SOURCE_URL}/releases/tag/{tag}',
    }
