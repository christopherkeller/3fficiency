from status.models import User, Status, Role, Group, Membership
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render_to_response
from django.core import serializers
from django.core.context_processors import csrf

def status_detail(request, status_id):
    status_details = Status.objects.get(id=status_id)
    response = TemplateResponse(request, 'status_details.html', { 'status_details': status_details })
    return response 


@login_required
def index(request):
	groups = [] 
	user_status = {}
	membership = Membership.objects.filter(user__id=request.user.id)
	for m in membership:
		groups.append(Membership.objects.filter(group__id=m.group.id))

        response = TemplateResponse(request, 'index.html', { 'membership': membership, 'groups': groups })
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

@login_required
def playground(request):
	ctx = {}
	ctx['user'] = request.user
	ctx['csrf'] = csrf(request)
	return render_to_response('playground.html', ctx)

def get_latest_status_by_user_tag(request, format):
	if format == 'json':
		mimetype = 'application/json'

	hashTag = request.POST['hashTag']

	data = serializers.serialize(format
		, Status.objects.filter(
			user__id=request.user.id
		).filter(
			group__group_name=hashTag
		).order_by(
			'-date'
		)[:1])

	if request.method == 'POST':
		return HttpResponse(data, mimetype)
