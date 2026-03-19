import json
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CustomPasswordChangeForm, EditProfileForm, LoginForm, RegisterForm
from .models import Skill

User = get_user_model()
USERS_PER_PAGE = 12
SKILLS_AUTOCOMPLETE_LIMIT = 10


def paginate(queryset, request, per_page=USERS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("projects:project_list"))
        return render(request, "users/register.html", {"form": form})
    form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user:
                login(request, user)
                return redirect(reverse("projects:project_list"))
            form.add_error(None, "Неверный имейл или пароль")
        return render(request, "users/login.html", {"form": form})
    form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(reverse("projects:project_list"))


def participants_view(request):
    skill_name = request.GET.get("skill", "")
    all_skills = Skill.objects.all()
    participants = User.objects.filter(is_active=True).order_by("-id")
    active_skill = None
    if skill_name:
        participants = participants.filter(skills__name=skill_name)
        active_skill = skill_name
    page_obj = paginate(participants, request)
    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"profile_user": profile_user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse("users:user_detail", kwargs={"user_id": request.user.pk}))
        return render(request, "users/edit_profile.html", {"form": form})
    form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            login(request, request.user)
            return redirect(reverse("users:user_detail", kwargs={"user_id": request.user.pk}))
        return render(request, "users/change_password.html", {"form": form})
    form = CustomPasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def skills_autocomplete(request):
    q = request.GET.get("q", "")
    skills = Skill.objects.filter(name__istartswith=q).order_by("name")[:SKILLS_AUTOCOMPLETE_LIMIT]
    data = [{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
def add_skill_view(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user != request.user:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
    try:
        import json
        body = json.loads(request.body)
        skill_id = body.get("skill_id")
        name = body.get("name", "").strip()
    except Exception:
        skill_id = request.POST.get("skill_id")
        name = request.POST.get("name", "").strip()

    created = False
    added = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "No skill_id or name provided"}, status=HTTPStatus.BAD_REQUEST)

    if skill not in profile_user.skills.all():
        profile_user.skills.add(skill)
        added = True

    return JsonResponse({"skill_id": skill.id, "id": skill.id, "name": skill.name,
                         "created": created, "added": added})


@login_required
def remove_skill_view(request, user_id, skill_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user != request.user:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
    skill = get_object_or_404(Skill, pk=skill_id)
    profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
