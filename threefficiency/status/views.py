from status.models import User, Status, Role, Group, Membership
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render_to_response
from django.core import serializers
from django.core.context_processors import csrf
import json
import datetime

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

def get_all_status_by_user(request, user_name, group_name, format):
	if format == 'json':
		mimetype = 'application/json'

	data = serializers.serialize(format,
		Status.objects.filter(
			user__id=User.objects.filter(user_name=user_name)[0].id
		).filter(
			group__id=Group.objects.filter(group_name=group_name)[0].id
		)) 

	return HttpResponse(data, mimetype)

def get_all_status_by_group(request, group_name, time_frame, format):
	if format == 'json':
		mimetype = 'application/json'

	# for now time_frame will be in days (7, 23, etc)

	today = datetime.date.today()
	days_ago = today - datetime.timedelta(days=int(time_frame))

	all_objects = {}
	all_objects['keys'] = []

	for s in Status.objects.filter(group__id=Group.objects.filter(group_name=group_name)[0].id).filter(date__gt=days_ago):
		user = "%s %s" % (s.user.first_name, s.user.last_name)
		if user in all_objects:
			all_objects[user].append([s.date.strftime('%m/%d/%Y'), s.completed_status]) 
		else:
			all_objects[user] = []
			all_objects[user].append([s.date.strftime('%m/%d/%Y'), s.completed_status]) 
			all_objects['keys'].append(user)

	if len(all_objects['keys']) == 0:
		for m in Membership.objects.filter(group__id=Group.objects.filter(group_name=group_name)[0].id):
			user = "%s %s" % (m.user.first_name, m.user.last_name)

			if user not in all_objects:
				all_objects[user] = []
				all_objects[user].append(['', 'no status for the given timeframe']) 
				all_objects['keys'].append(user)
			
			
		


	return HttpResponse(json.dumps(all_objects), mimetype)
