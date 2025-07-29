from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from .decorators import tipo_usuario_requerido
from .models import Usuario
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UsuarioCreateForm

class LoginCustomView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('campanhas_listagem')  # nome da url
    redirect_authenticated_user = False 

    def form_invalid(self, form):
        messages.error(self.request, "Usuário ou senha inválidos.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('campanha_list')
    



@login_required(login_url='login')
@tipo_usuario_requerido('master')
def admin_usuarios_view(request):
    usuarios = Usuario.objects.exclude(id=request.user.id)

    if request.method == 'POST':

        # ✅ EXCLUSÃO DE USUÁRIO
        if 'delete_user_id' in request.POST:
            delete_id = request.POST.get('delete_user_id')
            try:
                user = Usuario.objects.get(id=delete_id)
                user.delete()  # remove do banco e credenciais
                messages.success(request, f"Usuário {user.username} excluído com sucesso.")
            except Usuario.DoesNotExist:
                messages.error(request, "Usuário não encontrado para exclusão.")
            return redirect('admin_usuarios')

        # ✅ ALTERAÇÃO DE TIPO
        if 'user_id' in request.POST:
            user_id = request.POST.get('user_id')
            novo_tipo = request.POST.get('tipo')
            try:
                user = Usuario.objects.get(id=user_id)
                if user.tipo != novo_tipo:
                    user.tipo = novo_tipo
                    user.save()
                    messages.success(request, f"Permissão de {user.username} alterada para {novo_tipo}.")
            except Usuario.DoesNotExist:
                messages.error(request, "Usuário não encontrado.")
            return redirect('admin_usuarios')

        # ✅ CRIAÇÃO DE USUÁRIO
        form_criacao = UsuarioCreateForm(request.POST)
        if form_criacao.is_valid():
            form_criacao.save()
            messages.success(request, "Usuário criado com sucesso.")
            return redirect('admin_usuarios')
        else:
            return render(request, 'admin_usuarios.html', {
                'usuarios': usuarios,
                'form_criacao': form_criacao
            })

    return render(request, 'admin_usuarios.html', {
        'usuarios': usuarios,
        'form_criacao': UsuarioCreateForm()
    })