import csv
import openpyxl 
from datetime import datetime
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import login, update_session_auth_hash
from django.utils.crypto import get_random_string
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .models import Chamado, Comentario, Setor, Perfil
from .forms import ChamadoForm, ComentarioForm, SetorForm, UsuarioCompletoForm
from .utils import calcular_prazo_uteis


@login_required
def home(request):
    # processa as acoes em massa selecionadas na checkbox
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_tickets')
        action = request.POST.get('action')

        if not selected_ids:
            messages.warning(request, 'Nenhum chamado selecionado.')
            return redirect('home')

        if action == 'delete':
            # verifica permissao antes de sair apagando tudo
            if request.user.is_superuser or request.user.has_perm('tickets.delete_chamado'):
                Chamado.objects.filter(id__in=selected_ids).delete()
                messages.success(request, f'{len(selected_ids)} chamados excluídos!')
            else:
                messages.error(request, 'Ação negada: Visitantes não podem excluir chamados.')

        elif action == 'close':
            if request.user.is_superuser or request.user.has_perm('tickets.change_chamado'):
                Chamado.objects.filter(id__in=selected_ids).update(
                    status='FECHADO', 
                    data_atualizacao=timezone.now()
                )
                messages.success(request, f'{len(selected_ids)} chamados fechados!')
            else:
                messages.error(request, 'Ação negada: Você não tem permissão para fechar chamados.')

        elif action == 'progress':
            if request.user.is_superuser or request.user.has_perm('tickets.change_chamado'):
                Chamado.objects.filter(id__in=selected_ids).update(
                    status='ANDAMENTO',
                    data_atualizacao=timezone.now()
                )
                messages.success(request, f'{len(selected_ids)} chamados em andamento!')
            else:
                messages.error(request, 'Ação negada: Visitantes não podem alterar o status.')

        elif action == 'reopen':
            if request.user.is_superuser or request.user.has_perm('tickets.change_chamado'):
                Chamado.objects.filter(id__in=selected_ids).update(
                    status='ABERTO',
                    data_atualizacao=timezone.now()
                )
                messages.success(request, f'{len(selected_ids)} chamados reabertos!')
            else:
                messages.error(request, 'Ação negada: Você não tem permissão para reabrir chamados.')

        elif action == 'export_excel':
            response = HttpResponse(content_type='text/csv')
            filename = f"relatorio_chamados_{datetime.now().strftime('%d-%m-%Y_%H%M')}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # hackzinho pro excel entender os acentos em portugues
            response.write(u'\ufeff'.encode('utf8')) 

            writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['ID', 'Título', 'Prioridade', 'Status', 'Solicitante', 'Setor', 'Data Abertura', 'Última Atualização'])

            chamados_export = Chamado.objects.filter(id__in=selected_ids)
            for c in chamados_export:
                writer.writerow([
                    c.id, c.titulo, c.get_prioridade_display(), 
                    c.get_status_display(), c.usuario.username, 
                    c.setor.nome, c.data_criacao.strftime('%d/%m/%Y %H:%M'),
                    c.data_atualizacao.strftime('%d/%m/%Y %H:%M')
                ])
            return response

        elif action == 'export_pdf':
            response = HttpResponse(content_type='application/pdf')
            filename = f"relatorio_chamados_{datetime.now().strftime('%d-%m-%Y')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            doc = SimpleDocTemplate(response, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("Relatório de Chamados - PySupport", styles['Title']))
            elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", styles['Normal']))
            elements.append(Spacer(1, 20))

            data = [['ID', 'Título (Resumo)', 'Setor', 'Prioridade', 'Status', 'Aberto Em']]
            
            chamados_export = Chamado.objects.filter(id__in=selected_ids)
            for c in chamados_export:
                titulo_curto = c.titulo[:25] + '...' if len(c.titulo) > 25 else c.titulo
                data.append([
                    str(c.id), 
                    titulo_curto, 
                    c.setor.nome, 
                    c.get_prioridade_display(),
                    c.get_status_display(),
                    c.data_criacao.strftime('%d/%m/%Y %H:%M')
                ])

            table = Table(data, colWidths=[30, 160, 90, 70, 80, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
                ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ]))
            
            elements.append(table)
            doc.build(elements)
            return response

        return redirect('home')

    # superuser ve tudo, usuario comum so ve o que eh dele ou do setor dele
    if request.user.is_superuser:
        chamados_base = Chamado.objects.all()
    else:
        user_setor = request.user.perfil.setor if hasattr(request.user, 'perfil') else None
        chamados_base = Chamado.objects.filter(
            Q(usuario=request.user) | Q(setor=user_setor)
        ).distinct()

    # filtros da busca avancada
    search_query = request.GET.get('q')
    if search_query:
        if search_query.isdigit():
            chamados_base = chamados_base.filter(id=search_query)
        else:
            chamados_base = chamados_base.filter(
                Q(titulo__icontains=search_query) |
                Q(usuario__username__icontains=search_query) |
                Q(setor__nome__icontains=search_query)
            )

    prioridades = request.GET.getlist('prioridade')
    if prioridades:
        chamados_base = chamados_base.filter(prioridade__in=prioridades)

    data_filtro = request.GET.get('data_criacao')
    if data_filtro:
        chamados_base = chamados_base.filter(data_criacao__date=data_filtro)

    setor_id = request.GET.get('setor')
    if setor_id:
        chamados_base = chamados_base.filter(setor__id=setor_id)

    # contadores para o dashboard
    total_abertos = chamados_base.filter(status='ABERTO').count()
    total_andamento = chamados_base.filter(status='ANDAMENTO').count()
    total_solucionados = chamados_base.filter(status='SOLUCIONADO').count()
    total_fechados = chamados_base.filter(status='FECHADO').count()

    status_filter = request.GET.get('status')
    if status_filter:
        chamados_base = chamados_base.filter(status=status_filter)

    order_param = request.GET.get('order', 'recent')
    if order_param == 'oldest':
        chamados_base = chamados_base.order_by('data_criacao') 
    else:
        chamados_base = chamados_base.order_by('-data_criacao')

    paginator = Paginator(chamados_base, 10)
    chamados = paginator.get_page(request.GET.get('page'))

    setores = Setor.objects.all().order_by('nome')

    return render(request, 'tickets/home.html', {
        'chamados': chamados,
        'setores': setores,
        'total_abertos': total_abertos,
        'total_andamento': total_andamento,
        'total_solucionados': total_solucionados,
        'total_fechados': total_fechados,
        'search_query': search_query,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def gerenciar_setores(request):
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor cadastrado com sucesso!')
        else:
            messages.error(request, 'Setor inválido ou já existente.')
    return redirect('home')


@login_required
def novo_chamado(request):
    if request.method == 'POST':
        form = ChamadoForm(request.POST, request.FILES)
        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.usuario = request.user
            
            # define o prazo do sla dependendo da prioridade
            if chamado.prioridade == 'ALTA':
                horas_sla = 6
            elif chamado.prioridade == 'MEDIA':
                horas_sla = 16
            else: 
                horas_sla = 30 
            
            chamado.data_limite = calcular_prazo_uteis(datetime.now(), horas_sla)
            
            chamado.save()
            messages.success(request, 'Chamado aberto com sucesso!')
            return redirect('home')
    else:
        form = ChamadoForm()

    return render(request, 'tickets/novo_chamado.html', {'form': form})


@login_required
def editar_chamado(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    eh_dono = chamado.usuario == request.user

    eh_do_setor = (
        hasattr(request.user, 'perfil') and
        request.user.perfil.setor and
        chamado.setor == request.user.perfil.setor
    )

    # trava de seguranca: so entra quem criou, quem eh do setor ou admin
    if not (request.user.is_superuser or eh_dono or eh_do_setor):
        messages.error(request, "Você não tem permissão para visualizar este chamado.")
        return redirect('home')

    if request.method == 'POST':
        
        # cliente aprovando ou rejeitando a solucao
        if 'acao_usuario' in request.POST:
            acao = request.POST.get('acao_usuario')
            if eh_dono or request.user.is_superuser:
                if acao == 'aprovar':
                    chamado.status = 'FECHADO'
                    chamado.data_atualizacao = timezone.now()
                    chamado.save()
                    messages.success(request, "Chamado fechado com sucesso! Obrigado.")
                elif acao == 'rejeitar':
                    chamado.status = 'ANDAMENTO'
                    chamado.data_atualizacao = timezone.now()
                    chamado.save()
                    messages.warning(request, "Chamado reaberto para análise.")
            else:
                messages.error(request, "Apenas o solicitante pode aprovar ou rejeitar.")
            return redirect('editar_chamado', pk=pk)
        
        # tecnico marcou como resolvido
        elif 'btn_solucionar' in request.POST and (request.user.is_superuser or eh_do_setor):
            chamado.status = 'SOLUCIONADO'
            chamado.data_atualizacao = timezone.now()
            chamado.save()
            messages.info(request, "Chamado marcado como solucionado. Aguardando aprovação do cliente.")
            return redirect('editar_chamado', pk=pk)

        elif 'btn_editar' in request.POST:
            form = ChamadoForm(request.POST, request.FILES, instance=chamado)
            if form.is_valid():
                # forca a atualizacao da data ao editar
                obj_chamado = form.save(commit=False)
                obj_chamado.data_atualizacao = timezone.now()
                obj_chamado.save()
                messages.success(request, 'Alterações salvas!')
                return redirect('editar_chamado', pk=pk)
        
        elif 'btn_comentar' in request.POST:
            form_comentario = ComentarioForm(request.POST, request.FILES)
            if form_comentario.is_valid():
                comentario = form_comentario.save(commit=False)
                comentario.chamado = chamado
                comentario.usuario = request.user
                comentario.save()

                # importante: atualiza a data do chamado quando rola um comentario novo
                chamado.data_atualizacao = timezone.now()
                chamado.save()

                return redirect('editar_chamado', pk=pk)

    form = ChamadoForm(instance=chamado)
    form_comentario = ComentarioForm()

    return render(request, 'tickets/editar_chamado.html', {
        'chamado': chamado,
        'form': form,
        'comentarios': chamado.comentarios.all().order_by('data'),
        'form_comentario': form_comentario,
    })


@login_required
def excluir_chamado(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    if request.user.is_superuser or request.user.has_perm('tickets.delete_chamado'):
        chamado.delete()
        messages.success(request, 'Chamado excluído.')
    return redirect('home')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def gerenciar_usuarios(request, user_id=None):
    usuarios = User.objects.all().select_related('perfil').order_by('first_name')
    
    # busca as permissoes para popular o modal de grupos
    todas_permissoes = Permission.objects.all().select_related('content_type').order_by(
        'content_type__app_label', 'content_type__model', 'codename'
    )

    usuario_selecionado = None
    form = None
    modo_novo = request.GET.get('novo') == '1'

    if modo_novo:
        form = UsuarioCompletoForm()
    elif user_id:
        usuario_selecionado = get_object_or_404(User, pk=user_id)
        form = UsuarioCompletoForm(
            instance=usuario_selecionado,
            initial={
                'setor': getattr(usuario_selecionado.perfil, 'setor', None),
                'grupo': usuario_selecionado.groups.first(),
            }
        )

    return render(request, 'tickets/gerenciar_usuarios.html', {
        'usuarios': usuarios,
        'usuario_selecionado': usuario_selecionado,
        'form': form,
        'modo_novo': modo_novo,
        'setores': Setor.objects.all(),
        'grupos': Group.objects.all(),
        'todas_permissoes': todas_permissoes, 
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def exportar_usuarios(request):
    formato = request.GET.get('format')
    usuarios = User.objects.all().order_by('first_name')
    
    if formato == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="usuarios_{timezone.now().strftime("%d-%m-%Y")}.xlsx"'

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Colaboradores"

        columns = ['Nome Completo', 'Usuário', 'E-mail', 'Setor', 'Status', 'Data Cadastro']
        ws.append(columns)

        for user in usuarios:
            setor = getattr(user, 'perfil', None) and getattr(user.perfil, 'setor', None)
            ws.append([
                user.get_full_name() or user.username,
                user.username,
                user.email,
                str(setor) if setor else "Não definido",
                "Ativo" if user.is_active else "Inativo",
                user.date_joined.strftime('%d/%m/%Y')
            ])

        wb.save(response)
        return response

    return HttpResponse("Formato inválido", status=400)


@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def acao_em_massa_usuarios(request):
    action = request.POST.get('action_type')
    user_ids = request.POST.getlist('selected_users')

    if not user_ids:
        messages.warning(request, "Nenhum usuário selecionado.")
        return redirect('gerenciar_usuarios')

    if action == 'delete':
        # nao deixa o admin apagar a si mesmo
        users_to_delete = User.objects.filter(id__in=user_ids).exclude(id=request.user.id)
        count = users_to_delete.count()
        
        if count > 0:
            users_to_delete.delete()
            messages.success(request, f"{count} usuários excluídos.")
        else:
            messages.warning(request, "Não foi possível excluir os usuários selecionados.")

    return redirect('gerenciar_usuarios')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def criar_usuario_sistema(request):
    if request.method == 'POST':
        form = UsuarioCompletoForm(request.POST)
        if form.is_valid():
            # salva o user, depois vincula grupo e perfil
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            user.groups.add(form.cleaned_data['grupo'])

            Perfil.objects.create(
                user=user,
                setor=form.cleaned_data['setor'],
                trocar_senha=True
            )

            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            return redirect('gerenciar_usuarios')

    return redirect('gerenciar_usuarios')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def editar_usuario_post(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.email = request.POST.get('email')
        usuario.save()

        # garante que o perfil exista antes de salvar o setor
        perfil, _ = Perfil.objects.get_or_create(user=usuario)
        setor_id = request.POST.get('setor')
        if setor_id:
            perfil.setor = Setor.objects.get(pk=setor_id)
        perfil.save()

        messages.success(request, f'Dados de {usuario.username} atualizados!')

    return redirect('gerenciar_usuarios', user_id=user_id)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def alternar_status_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if usuario == request.user:
        messages.error(request, 'Ação proibida.')
    else:
        usuario.is_active = not usuario.is_active
        usuario.save()
        messages.success(request, f'Status de {usuario.username} alterado.')

    return redirect('gerenciar_usuarios', user_id=usuario.id)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def excluir_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario != request.user:
        usuario.delete()
        messages.success(request, 'Usuário removido.')
    return redirect('gerenciar_usuarios')


@login_required
def perfil_trocar_senha(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # mantem logado apos mudar senha

            request.user.perfil.trocar_senha = False
            request.user.perfil.save()

            messages.success(request, 'Senha atualizada!')
            return redirect('home')
        else:
            messages.error(request, 'Erro na validação.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'tickets/trocar_senha.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def criar_grupo_sistema(request):
    if request.method == 'POST':
        nome_grupo = request.POST.get('nome_grupo')
        permissoes_ids = request.POST.getlist('permissoes_escolhidas')

        if nome_grupo:
            grupo, created = Group.objects.get_or_create(name=nome_grupo)
            
            if permissoes_ids:
                grupo.permissions.set(permissoes_ids)
            
            grupo.save()

            if created:
                messages.success(request, f'Grupo "{nome_grupo}" criado com {len(permissoes_ids)} permissões!')
            else:
                messages.warning(request, f'Grupo "{nome_grupo}" atualizado.')
        else:
            messages.error(request, 'O nome do grupo é obrigatório.')
            
    return redirect('gerenciar_usuarios')


def criar_usuario_teste(request):
    sufixo = get_random_string(5)
    user = User.objects.create_user(
        username=f'visitante_{sufixo}',
        password='123'
    )
    Perfil.objects.create(user=user, trocar_senha=False)
    login(request, user)
    return redirect('home')


def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Perfil.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/registro.html', {'form': form})