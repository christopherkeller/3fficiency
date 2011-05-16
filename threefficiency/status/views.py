from status.models import User, Status, Role, Group, Membership, Graph
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
	# need to set some cookies so we know who is logged in
	ownership = Graph.objects.filter(end_vertex=request.user.user_name).filter(hops=0)
	groups = Graph.objects.filter(start_vertex=request.user.user_name).filter(hops=0)

        response = TemplateResponse(request, 'index.html', { 'groups': groups, 'ownership': ownership })
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

# this should return a list of users that are writing status to a 
# group that they are not members of. The owner of the group will need
# to approve them for them to view the request
# owner == the username of the owner of the group
def new_requests(request, manager_username, format):
	if format == 'json':
		mimetype = 'application/json'

	if request.method == 'GET':
		users = [] 
		# find all the groups that you are the owner of
		for group in Graph.objects.filter(end_vertex=manager_username).filter(hops=0):

		# find all the status for each of the groups that you are an owner of. Only need the usernames
			group_id = Group.objects.filter(group_name=group.start_vertex)[0].id	
			for status in Status.objects.filter(group__id=group_id):
				# loop through all the users that reported status and then check to see if they are members
				# whoever is not return them, they need to be approved or denided 
				if len(Graph.objects.filter(start_vertex=status.user.user_name).filter(hops=0)) == 0:
				# skip the owner, who is not a member of the group via the graph
					if status.user.user_name != manager_username:
						users.append({ 'first_name': status.user.first_name, 'last_name': status.user.last_name, 'id': status.user.id, 'user_name': status.user.user_name, 'group': group.start_vertex })

		return HttpResponse(json.dumps(users), mimetype)
	elif request.method == 'POST':
		new_requests_post_data = request.POST
		user_id = new_requests_post_data['user_id']
		response = new_requests_post_data['response']
		group = new_requests_post_data['group']
		user = User.objects.filter(id=user_id)[0]
		if response == 'approve':
			# ok we approve this user 
			new_member = Graph.objects.create(start_vertex=user.user_name, end_vertex=group, hops=0, source='3f')	
			new_member_step2 = Graph.objects.create(start_vertex=user.user_name, end_vertex=manager_username, hops=1, source='3f')
			# now add in edges
			# this seems really lame, since rails can do this much cleaner
			new_member.save	
			new_member_step2.save	
			Graph.objects.filter(id=new_member.id).update(entry_edge_id=new_member.id, direct_edge_id=new_member.id, exit_edge_id=new_member.id)
			Graph.objects.filter(id=new_member_step2.id).update(entry_edge_id=new_member_step2.id, direct_edge_id=new_member_step2.id, exit_edge_id=new_member_step2.id)
		
		user_feedback = "%s %s has been %s" %(user.first_name, user.last_name, response)
		response_data = { 'user_name': user.user_name, 'user_feedback': user_feedback }
		return HttpResponse(json.dumps(response_data), mimetype)
		
	

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
