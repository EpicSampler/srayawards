from django.db import models
from django.utils import timezone

class Nomination(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название номинации")
    description = models.TextField(verbose_name="Описание номинации")
    image = models.ImageField(upload_to='nominations/', null=True, blank=True, verbose_name="Изображение номинации")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True)
    voting_end_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания голосования")
    
    def __str__(self):
        return self.title
    
    def is_voting_active(self):
        if self.voting_end_date:
            return timezone.now() < self.voting_end_date
        return self.is_active
    
    class Meta:
        verbose_name = "Номинация"
        verbose_name_plural = "Номинации"
        ordering = ['-created_at']

class Candidate(models.Model):
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE, verbose_name="Номинация")
    name = models.CharField(max_length=200, verbose_name="Имя кандидата")
    description = models.TextField(verbose_name="Описание кандидата")
    photo = models.ImageField(upload_to='candidates/', null=True, blank=True, verbose_name="Фото")
    vote_count = models.IntegerField(default=0, verbose_name="Количество голосов")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.nomination.title}"
    
    @property
    def vote_percentage(self):
        total_votes = self.nomination.candidate_set.aggregate(total=models.Sum('vote_count'))['total'] or 0
        if total_votes > 0:
            return round((self.vote_count / total_votes * 100), 1)
        return 0
    
    class Meta:
        verbose_name = "Кандидат"
        verbose_name_plural = "Кандидаты"
        ordering = ['-vote_count']

class Vote(models.Model):
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE, verbose_name="Номинация")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, verbose_name="Кандидат")
    ip_address = models.GenericIPAddressField(verbose_name="IP адрес")
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name="Время голосования")
    
    def __str__(self):
        return f"Голос за {self.candidate.name} от {self.ip_address}"
    
    class Meta:
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"
        unique_together = ['nomination', 'ip_address']
        ordering = ['-voted_at']
