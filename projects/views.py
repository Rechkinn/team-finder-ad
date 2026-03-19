from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ProjectForm
from .models import Project

PROJECTS_PER_PAGE = 12
PROJECT_STATUS_OPEN = "open"


def paginate(queryset, request, per_page=PROJECTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def project_list_view(request):
    projects = Project.objects.select_related("owner").order_by("-created_at")
    page_obj = paginate(projects, request)
    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(reverse("projects:project_detail", kwargs={"project_id": project.pk}))
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": False},
        )
    form = ProjectForm()
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(reverse("projects:project_detail", kwargs={"project_id": project.pk}))
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True},
        )
    form = ProjectForm(instance=project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required
def complete_project_view(request, project_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse({"error": "Project is already closed"}, status=HTTPStatus.BAD_REQUEST)
    project.status = "closed"
    project.save()
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
def toggle_participate_view(request, project_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    is_participant = project.participants.filter(id=user.id).exists()
    if is_participant:
        project.participants.remove(user)
        participating = False
    else:
        project.participants.add(user)
        participating = True
    return JsonResponse({"status": "ok", "participating": participating})


@login_required
def toggle_favorite_view(request, project_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    is_favorited = project.favorited_by.filter(id=user.id).exists()
    if is_favorited:
        project.favorited_by.remove(user)
        favorited = False
    else:
        project.favorited_by.add(user)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
def favorite_projects_view(request):
    projects = request.user.favorite_projects.order_by("-created_at")
    page_obj = paginate(projects, request)
    return render(
        request, "projects/favorite_projects.html", {"projects": page_obj}
    )
