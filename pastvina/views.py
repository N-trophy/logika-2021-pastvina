from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.static import serve
from pastvina.models import MediaFile, StaticPage, Contribution
from pastvina.templatetags.extras import gen_file_refs, markdown_to_html


def page_index(request):
    """
    Renders the index page from template. If CONTEST_REDIRECT is set, the main page of that contast is rendered instead.

    template: pastvina/index.html

    Privacy policy: PUBLIC

    :param request: HTTP request
    :return: HTTP response
    """
    contribs = Contribution.public_objects().order_by('-public_from')[:5]
    return render(request, 'pastvina/index.html', {
        'contribs': contribs,
        'navbar_absolute_pos': True,
    })


def page_login(request):
    """
    POST: Logs a user in and redirects to 'index' or reponses HttpResponseBadRequest if data are invalid.

    GET: Renders a login form.

    Template: seminar_contest/login.html

    Privacy policy: PUBLIC

    :param request: HTTP request
    :return: HTTP response
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            if request.GET.get('text_only'):
                return HttpResponseBadRequest('Přihlašovací jméno nebo heslo není správné.')
            else:
                messages.error(request, 'Přihlašovací jméno nebo heslo není správné.')
                return render(request, "pastvina/login.html", {'navbar_absolute_pos': True})
    else:
        return render(request, "pastvina/login.html", {'navbar_absolute_pos': True})


@login_required()
def handler_logout(request):
    """
    Logs a user out and redirects to 'index'.

    Privacy policy: LOGIN_REQUIRED

    :param request: HTTP request
    :return: HTTP response
    """
    logout(request)
    return redirect('/')


@login_required
def protected_serve(request, path, document_root=None, show_indices=None):
    """
    Serves a file from the private storage. The file is returned only if it's requested by its owner or by an admin.

    Privacy policy: LOGIN REQUIRED

    :param request: HTTP request
    :param path: Path to the file
    :param document_root: Prefix to be prepended to the path
    :return: HTTP response
    """
    try:
        owner_id = int(MediaFile.userid_from_filename(path.split('/')[-1]))
    except ValueError:
        owner_id = None

    if request.user.is_staff or (owner_id is not None and request.user.id == owner_id):
        return serve(request, path, document_root, show_indices)
    else:
        return HttpResponseForbidden()


def page_static(request, path):
    page = get_object_or_404(StaticPage, endpoint='/' + path)

    return render(request, 'pastvina/static_page.html', {'page': page})


def handler_markdown_to_html(request):
    text = request.body.decode('utf-8')
    html = markdown_to_html(gen_file_refs(text))
    return HttpResponse(html)
