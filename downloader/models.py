from django.db import models
from django.contrib.auth.models import Permission,User

class Video(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
	video = models.CharField(max_length=255)
	date = models.DateField()

	def __str__(self):
		return self.user.username+" "+self.video

