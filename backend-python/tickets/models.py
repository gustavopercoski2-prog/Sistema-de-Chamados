from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Setor(models.Model):
    # setores para organizar os chamados por area
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'


class Perfil(models.Model):
    # estende o usuario padrao do django para vincular a um setor
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True)
    trocar_senha = models.BooleanField(default=True)

    def __str__(self):
        setor = self.setor.nome if self.setor else 'sem setor'
        return f'{self.user.username} - {setor}'


class Chamado(models.Model):
    PRIORIDADES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]

    STATUS = [
        ('ABERTO', 'Aberto'),
        ('ANDAMENTO', 'Em andamento'),
        ('SOLUCIONADO', 'Solucionado'), 
        ('FECHADO', 'Fechado'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chamados_abertos'
    )
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()

    # se apagar o setor, o chamado continua existindo
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True)

    atribuido_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chamados_atribuidos'
    )

    arquivo = models.FileField(upload_to='anexos/', null=True, blank=True)
    prioridade = models.CharField(max_length=10, choices=PRIORIDADES, default='BAIXA')
    status = models.CharField(max_length=20, choices=STATUS, default='ABERTO')
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    # usado para mostrar o prazo na home
    data_limite = models.DateTimeField(null=True, blank=True) 
    
    # ordenacao correta na lista de chamados
    data_atualizacao = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # fallback caso a view nao calcule o sla corretamente
        if not self.id and not self.data_limite:
            agora = timezone.now()
            
            horas_sla = 30
            if self.prioridade == 'ALTA':
                horas_sla = 6
            elif self.prioridade == 'MEDIA':
                horas_sla = 16
            
            # calculo de horas corridas pra garantir que nao fique vazio
            self.data_limite = agora + timedelta(hours=horas_sla)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.id} - {self.titulo}'
    
    @property
    def estourou_prazo(self):
        # verifica se ja passou do prazo para pintar de vermelho no front
        if self.status == 'FECHADO' or not self.data_limite:
            return False
        return timezone.now() > self.data_limite


class Comentario(models.Model):
    # historico da conversa entre tecnico e solicitante
    chamado = models.ForeignKey(
        Chamado,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField(blank=True, null=True)
    arquivo = models.FileField(upload_to='comentarios/', null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'comentario de {self.usuario} no chamado #{self.chamado.id}'