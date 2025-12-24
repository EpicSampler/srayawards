from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Nomination, Candidate, Vote

def custom_404(request, exception):
    """Кастомная страница 404"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Кастомная страница 500"""
    return render(request, '500.html', status=500)

def index(request):
    """Главная страница со списком номинаций и правилами"""
    nominations = Nomination.objects.filter(is_active=True)
    return render(request, 'index.html', {'nominations': nominations})

def voting(request, nomination_id):
    """Страница голосования в конкретной номинации"""
    nomination = get_object_or_404(Nomination, id=nomination_id)
    candidates = nomination.candidate_set.all().order_by('-vote_count')
    
    # Используем свойство vote_percentage из модели
    for candidate in candidates:
        # Процент уже рассчитывается в модели
        pass
    
    # Проверка, голосовал ли пользователь
    user_voted = False
    user_vote = None
    
    # Получаем IP пользователя
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Проверяем, голосовал ли уже с этого IP
    if ip:
        user_vote = Vote.objects.filter(nomination=nomination, ip_address=ip).first()
        user_voted = user_vote is not None
    
    # Проверяем активность голосования
    is_voting_active = nomination.is_voting_active()
    
    context = {
        'nomination': nomination,
        'candidates': candidates,
        'user_voted': user_voted,
        'user_vote': user_vote,
        'is_voting_active': is_voting_active,
    }
    
    return render(request, 'voting.html', context)

def vote(request, nomination_id):
    """Обработка голосования"""
    if request.method == 'POST':
        nomination = get_object_or_404(Nomination, id=nomination_id)
        
        # Проверяем, активно ли голосование
        if not nomination.is_voting_active():
            messages.error(request, 'Голосование в этой номинации завершено.')
            return redirect('voting', nomination_id=nomination_id)
        
        # Получаем IP пользователя
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Проверяем, голосовал ли уже с этого IP
        if ip and Vote.objects.filter(nomination=nomination, ip_address=ip).exists():
            messages.error(request, 'Вы уже голосовали в этой номинации.')
            return redirect('voting', nomination_id=nomination_id)
        
        candidate_id = request.POST.get('candidate_id')
        candidate = get_object_or_404(Candidate, id=candidate_id, nomination=nomination)
        
        # Создаем запись о голосовании
        Vote.objects.create(
            nomination=nomination,
            candidate=candidate,
            ip_address=ip
        )
        
        # Обновляем счетчик голосов
        candidate.vote_count += 1
        candidate.save()
        
        messages.success(request, f'Ваш голос за {candidate.name} учтен!')
        
        return redirect('voting', nomination_id=nomination_id)
    
    return redirect('voting', nomination_id=nomination_id)
