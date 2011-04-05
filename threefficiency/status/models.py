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

class StatusForm(ModelForm):
        class Meta:
                model = Status 
