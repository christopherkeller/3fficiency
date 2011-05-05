from django.db import models
from django.forms import ModelForm

# Create your models here.
class User(models.Model):
  first_name = models.CharField(max_length=26)
  last_name = models.CharField(max_length=26)
  user_name = models.CharField(max_length=26)
  password_hash = models.CharField(max_length=100)
  password_salt = models.CharField(max_length=10)
  is_active = True
  
  def is_authenticated(self):
    return True
  
  def __unicode__(self):
    return "%s %s (%s)" % (self.first_name, self.last_name, self.user_name)

	
  class Meta:
	db_table = 'user'

class Graph(models.Model):
  start_vertex = models.CharField(max_length=36)
  end_vertex = models.CharField(max_length=36)
  hops = models.FloatField()

  def __unicode__(self):
	return "%s %s" % (self.start_vertex, self.end_vertex)

  class Meta:
	db_table = 'graph'

class Group(models.Model):
  group_name = models.CharField(max_length=26)
  is_public = models.BooleanField()

  def __unicode__(self):
    return self.group_name

  class Meta:
	db_table = 'groups'

class Role(models.Model):
  name = models.CharField(max_length=20)

  def __unicode__(self):
    return self.name

  class Meta:
	db_table = 'role'

class Status(models.Model):
  user = models.ForeignKey(User)
  group = models.ForeignKey(Group)
  date = models.DateTimeField('date')
  completed_status = models.CharField(max_length=3000)
  predicted_status = models.CharField(max_length=3000)

  def __unicode__(self):
    return "%s %s" % (self.user, self.completed_status) 

  class Meta:
	db_table = 'status'
  
class Membership(models.Model):
  user = models.ForeignKey(User)
  group = models.ForeignKey(Group)
  role = models.ForeignKey(Role)

  def __unicode__(self):
    return "%s has the %s role in the %s group" % (self.user, self.role, self.group) 

  class Meta:
	db_table = 'membership'

  def latest_status(self):
	latest_status = ''
	try:
		status = Status.objects.filter(user__id=self.user.id).filter(group__id=self.group.id).order_by('date')[0]
        	latest_status = "%s (%s)" %(status.completed_status, status.date)
        except IndexError, exc:
		latest_status = "No status given for this group yet"
	return latest_status 

class StatusForm(ModelForm):
        class Meta:
                model = Status 
