# Create your views here.
from threefficiency.models import User, Status, Role, Group, Membership
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def index(request):
        response = TemplateResponse(request, 'index.html', {})
        return response

@login_required
def status(request):
        user = request.user
        groups = Membership.objects.filter(user__id=user.id)
        user_status = Status.objects.filter(user__id=user.id)
        response = TemplateResponse(request, 'status.html', { 
                'page_title': 'Status', 
                'user': user,
                'groups' : groups,
                'user_status' : user_status
        })
        return response

def login(request):
  return HttpResponse("Login here")
