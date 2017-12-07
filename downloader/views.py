from django.http import HttpResponse
from django.http import Http404
from django.template import loader
from pytube import YouTube
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.views import generic
from django.views.generic import View
from .forms import UserForm
from .models import Video
from django.contrib.auth.models import User,Permission
import datetime

def index(request):
	template = loader.get_template('downloader/index.html') 
	context = {}
	return HttpResponse(template.render(context,request))

def details(request):
	if not request.user.is_authenticated():
		return render(request,'downloader/login.html',{'error_message':'You must login to access this feature'})
	else:
		template = loader.get_template('downloader/wizzyDownload.html') 
		context = {}
		return HttpResponse(template.render(context,request))

def profile(request):
	if not request.user.is_authenticated():
		return render(request,'downloader/login.html',{'error_message':'You must login to access this feature'})
	template = loader.get_template('downloader/profile.html')
	name = request.session["curr_user"]
	u = User.objects.get(username = name)
	vidlist = u.video_set.all()
	if len(vidlist) > 6:
			vidlist = vidlist[len(vidlist)-6:]
	context = {"user":u,"all_video" : vidlist}
	return HttpResponse(template.render(context,request))

def download(request):
	id = request.GET['url']
	#print("The String to be Downloaded is :: "+id)
	try:
		yt = YouTube(str(id)).streams.first().download()
		#yt = YouTube(id)
		#print(" Video : "+str(yt.filter('mp4')[-1]))
		#video = yt.filter('mp4')[-1]
		#video.download('/tmp/')
		message="Download Complete"
		#putting the song into the database
		name = request.session["curr_user"]
		u = User.objects.get(username=name)
		v = Video()
		v.user = u
		v.date = datetime.datetime.now().date()
		v.video = id
		v.save()
	except Exception as e:
		print(""+str(e))
		message = "Please enter a valid url Or check your Internet Connection"
		return render(request,'downloader/wizzyDownload.html',{'message':message})
	return render(request,'downloader/wizzyDownload.html',{'message':message})

class UserFormView(View):
	form_class = UserForm
	template_name = 'downloader/registration_form.html'
	def get(self,request):
		form = self.form_class(None)
		return render(request,self.template_name,{'form':form})

	def post(self,request):
		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.save(commit = False)
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()

			user = authenticate(username=username,password=password)
			if user is not None:
				if user.is_active:
					login(request,user)
					request.session['curr_user']=username
					return redirect('downloader:index')

		return render(request,self.template_name,{'form':form})

def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				request.session['curr_user']=username
				return render(request,'downloader/index.html')
			else:
				return render(request,'downloader/login.html',{'error_message':'Your account has been disabled'})
		else:
			return render(request,'downloader/login.html',{'error_message':'Invalid login'})
	return render(request,'downloader/login.html')

def logout_user(request):
	if "curr_user" in request.session:
		del request.session['curr_user']
	logout(request)
	form = UserForm(request.POST or None)
	context = {
		"form":form,
	}
	return render(request,'downloader/login.html',context)
