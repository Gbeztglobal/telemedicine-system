from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User

@login_required
def video_call(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    return render(request, 'chat/video_call.html', {'target_user': target_user})
