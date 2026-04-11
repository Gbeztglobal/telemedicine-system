from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import User

@login_required
def video_call(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    return render(request, 'chat/video_call.html', {'target_user': target_user})

@login_required
def chat_room(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    # Fetch last 50 messages
    from .models import Message
    from django.db.models import Q
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=target_user)) |
        (Q(sender=target_user) & Q(receiver=request.user))
    ).order_by('timestamp')[:50]
    
    return render(request, 'chat/chat_room.html', {
        'target_user': target_user,
        'chat_messages': messages
    })

@login_required
def upload_voice_note(request):
    if request.method == 'POST' and request.FILES.get('voice_note'):
        from .models import Message
        receiver_id = request.POST.get('receiver_id')
        receiver = get_object_or_404(User, id=receiver_id)
        
        msg = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            voice_note=request.FILES['voice_note']
        )
        return JsonResponse({'status': 'success', 'url': msg.voice_note.url})
    return JsonResponse({'status': 'error'}, status=400)
