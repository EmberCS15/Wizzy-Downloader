from pytube import YouTube
from django import template

register = template.Library()

@register.simple_tag
def get_videolist(id):
	yt=YouTube(id)
	ytList=yt.get_videos()
	return ytList