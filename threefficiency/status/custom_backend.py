import hashlib
from django.conf import settings
from status.models import User

class CustomBackend:
	supports_object_permissions = False
  	supports_anonymous_user = False
  	supports_inactive_user = False

	def authenticate(self, username=None, password=None):
		try:
			user = User.objects.get(user_name=username)
		except User.DoesNotExist:
			return None

		salted_password = user.password_salt + password
		hashed_password = hashlib.sha1(salted_password).hexdigest()
		
		if user.password_hash == hashed_password:
			return user
		
		return None

	def get_user(self, user_id):
		try:
      			return User.objects.get(pk=user_id)
    		except User.DoesNotExist:
      			return None
