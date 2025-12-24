from django.contrib import admin
from django.utils.html import format_html
from .models import Nomination, Candidate, Vote
import django.db.models as models

class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1
    fields = ['name', 'description', 'photo', 'vote_count']
    readonly_fields = ['vote_count']

class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ['ip_address', 'voted_at']
    can_delete = False

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'voting_end_date', 'candidate_count', 'total_votes', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'total_votes_display']
    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'description', 'image']
        }),
        ('Настройки голосования', {
            'fields': ['is_active', 'voting_end_date']
        }),
        ('Статистика', {
            'fields': ['created_at', 'total_votes_display']
        }),
    ]
    inlines = [CandidateInline]
    
    def candidate_count(self, obj):
        return obj.candidate_set.count()
    candidate_count.short_description = 'Кандидатов'
    
    def total_votes(self, obj):
        return obj.candidate_set.aggregate(total=models.Sum('vote_count'))['total'] or 0
    total_votes.short_description = 'Всего голосов'
    
    def total_votes_display(self, obj):
        total = self.total_votes(obj)
        return f"{total} голосов"
    total_votes_display.short_description = 'Всего голосов'

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'nomination', 'vote_count', 'vote_percentage', 'photo_preview']
    list_filter = ['nomination', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['vote_count', 'vote_percentage', 'created_at', 'photo_preview']
    fieldsets = [
        ('Основная информация', {
            'fields': ['nomination', 'name', 'description']
        }),
        ('Фотография', {
            'fields': ['photo', 'photo_preview']
        }),
        ('Статистика', {
            'fields': ['vote_count', 'vote_percentage', 'created_at']
        }),
    ]
    inlines = [VoteInline]
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = 'Предпросмотр фото'
    
    def vote_percentage(self, obj):
        return f"{obj.vote_percentage}%"
    vote_percentage.short_description = 'Процент голосов'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'nomination', 'ip_address', 'voted_at']
    list_filter = ['nomination', 'voted_at']
    search_fields = ['candidate__name', 'ip_address']
    readonly_fields = ['voted_at']
    
    def nomination(self, obj):
        return obj.candidate.nomination
    nomination.short_description = 'Номинация'
