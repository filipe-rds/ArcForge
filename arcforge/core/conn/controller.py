from arcforge.core.conn import Validator, HtmlResponse, RedirectResponse
from arcforge.core.conn.handler import *
from abc import ABC, abstractmethod
from typing import Type, List, Dict, Any, Optional


class Controller:
    """
    Classe base para controladores.
    Todos os controladores devem herdar desta classe para registrar rotas.
    """
    def __init_subclass__(cls, **kwargs):
        """
        Ao definir uma subclasse de Controller, garante que todas as rotas decoradas
        dentro da classe sejam registradas automaticamente.
        """
        super().__init_subclass__(**kwargs)
        cls._register_routes()

    @classmethod
    def _register_routes(cls):
        """
        Registra automaticamente os métodos do controlador decorados com @RequestHandler.route.
        """
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, "_route_info"):
                path, method = attr._route_info
                RequestHandler.add_route(path, {method: attr})

class RestController(ABC):
    """
    Classe base para controladores.
    Todos os controladores devem herdar desta classe para registrar rotas.
    """
    _dao = None
    _list_dto = None  # Opcional: DTO para listagem
    _detail_dto = None  # Opcional: DTO para detalhes

    def __init__(self):
        from arcforge.core.db.dao import DAO

        if self._dao is None:
            raise NotImplementedError("A classe concreta deve definir o atributo _dao")

        if not issubclass(self._dao, DAO):
            raise TypeError(f"A classe {self._dao.__name__} deve herdar da classe DAO")

        self._model = self._dao._model.__name__
        self._base_route = f"/{self._model.lower()}s"  # Rota padrão pluralizada

        # Registra as rotas CRUD padrão
        self._register_crud_routes()

    def __init_subclass__(cls, **kwargs):
        """
        Ao definir uma subclasse de Controller, garante que todas as rotas decoradas
        dentro da classe sejam registradas automaticamente.
        """
        super().__init_subclass__(**kwargs)
        cls._register_routes()

    @classmethod
    def _register_routes(cls):
        """
        Registra automaticamente os métodos do controlador decorados com @RequestHandler.route.
        """
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, "_route_info"):
                path, method = attr._route_info
                RequestHandler.add_route(path, {method: attr})

    def _register_crud_routes(self):
        """
        Registra as rotas CRUD padrão para o controlador.
        """
        # GET /recursos (listar todos)
        Router.route(self._base_route, "GET")(self.list_all)

        # GET /recursos/{id} (obter um)
        Router.route(f"{self._base_route}/{{id}}", "GET")(self.get_by_id)

        # POST /recursos (criar)
        Router.route(self._base_route, "POST")(self.create)

        # PUT /recursos/{id} (atualizar)
        Router.route(f"{self._base_route}/{{id}}", "PUT")(self.update)

        # DELETE /recursos/{id} (excluir)
        Router.route(f"{self._base_route}/{{id}}", "DELETE")(self.delete)

    def _serialize_list(self, items: List[Any]) -> List[Dict]:
        """
        Serializa uma lista de objetos usando o DTO de listagem, se disponível.
        """
        if self._list_dto:
            return [self._list_dto(item).to_dict() for item in items]
        return [item.to_dict() if hasattr(item, 'to_dict') else item.__dict__ for item in items]

    def _serialize_detail(self, item: Any) -> Dict:
        """
        Serializa um objeto usando o DTO de detalhes, se disponível.
        """
        if self._detail_dto:
            return self._detail_dto(item).to_dict()
        return item.to_dict() if hasattr(item, 'to_dict') else item.__dict__

    # Implementações das operações CRUD

    def list_all(self, request: Request) -> Response:
        """
        Lista todos os recursos.
        """
        items = self._dao.find_all()
        if items:
            serialized_items = self._serialize_list(items)
            return Response(HttpStatus.OK, serialized_items)
        return Response(HttpStatus.NOT_FOUND, {"error": f"Nenhum {self._model.lower()} encontrado"})

    @Validator(id=int)
    def get_by_id(self, request: Request, id) -> Response:
        """
        Obtém um recurso pelo ID.
        """
        item = self._dao.read(id)
        if item:
            serialized_item = self._serialize_detail(item)
            return Response(HttpStatus.OK, serialized_item)
        return Response(HttpStatus.NOT_FOUND, {"error": f"{self._model} não encontrado"})

    def create(self, request: Request) -> Response:
        """
        Cria um novo recurso.
        """
        data = request.body
        try:
            # Obtém a classe do modelo a partir do DAO
            model_class = self._dao._model
            # Cria instância do modelo usando os dados recebidos
            new_item = model_class(**data)
            # Salva no banco de dados
            saved_item = self._dao.save(new_item)
            # Serializa para a resposta
            serialized_item = self._serialize_detail(saved_item)
            return Response(HttpStatus.CREATED, serialized_item)
        except Exception as e:
            return Response(HttpStatus.BAD_REQUEST, {"error": str(e)})

    @Validator(id=int)
    def update(self, request: Request, id) -> Response:
        """
        Atualiza um recurso existente.
        """
        data = request.body
        try:
            # Verifica se o recurso existe
            existing_item = self._dao.read(id)
            if not existing_item:
                return Response(HttpStatus.NOT_FOUND, {"error": f"{self._model} não encontrado"})

            # Atualiza os atributos do recurso existente
            for key, value in data.items():
                if hasattr(existing_item, key):
                    setattr(existing_item, key, value)

            # Salva as alterações
            updated_item = self._dao.update(existing_item)
            serialized_item = self._serialize_detail(updated_item)
            return Response(HttpStatus.OK, serialized_item)
        except Exception as e:
            return Response(HttpStatus.BAD_REQUEST, {"error": str(e)})

    @Validator(id=int)
    def delete(self, request: Request, id) -> Response:
        """
        Exclui um recurso.
        """
        try:
            # Verifica se o recurso existe
            existing_item = self._dao.read(id)
            if not existing_item:
                return Response(HttpStatus.NOT_FOUND, {"error": f"{self._model} não encontrado"})

            # Exclui o recurso
            self._dao.delete(id)
            return Response(HttpStatus.NO_CONTENT, None)
        except Exception as e:
            return Response(HttpStatus.INTERNAL_SERVER_ERROR, {"error": str(e)})


class TemplateController(RestController):
    """
    Classe base para controladores que renderizam templates HTML.
    Herda do Controller básico e adiciona funcionalidades para renderização de templates.
    """
    _dao = None
    _list_template = None  # Template para listar todos os recursos
    _detail_template = None  # Template para exibir detalhes de um recurso
    _form_template = None  # Template para formulários (criar/editar)
    _error_template = None  # Template para erros (opcional)

    def __init__(self):
        super().__init__()

        # Verifica se o template engine está disponível
        from arcforge import template_engine  # Importação presumida
        self._template_engine = template_engine

        # Verifica se os templates obrigatórios foram definidos
        if self._list_template is None:
            self._list_template = f"{self._model.lower()}s.html"  # Padrão pluralizado

        if self._detail_template is None:
            self._detail_template = f"{self._model.lower()}_detail.html"

        if self._form_template is None:
            self._form_template = f"{self._model.lower()}_form.html"

        if self._error_template is None:
            self._error_template = "error.html"  # Template padrão para erros

    def _register_crud_routes(self):
        """
        Registra as rotas CRUD para o controlador de templates.
        Sobrescreve o método da classe pai para adicionar rotas específicas para templates.
        """
        # GET /recursos (listar todos via template)
        Router.route(self._base_route, "GET")(self.list_all_template)

        # GET /recursos/{id} (visualizar um via template)
        Router.route(f"{self._base_route}/{{id}}", "GET")(self.view_detail_template)

        # GET /recursos/novo (formulário para criar novo)
        Router.route(f"{self._base_route}/novo", "GET")(self.new_form_template)

        # POST /recursos (criar a partir do formulário)
        Router.route(self._base_route, "POST")(self.create_from_form)

        # GET /recursos/{id}/editar (formulário para editar)
        Router.route(f"{self._base_route}/{{id}}/editar", "GET")(self.edit_form_template)

        # POST /recursos/{id} (atualizar a partir do formulário)
        Router.route(f"{self._base_route}/{{id}}", "POST")(self.update_from_form)

        # GET /recursos/{id}/excluir (confirmação de exclusão)
        Router.route(f"{self._base_route}/{{id}}/excluir", "GET")(self.delete_confirm_template)

        # POST /recursos/{id}/excluir (excluir após confirmação)
        Router.route(f"{self._base_route}/{{id}}/excluir", "POST")(self.delete_from_form)

    def _render_error(self, status: HttpStatus, message: str) -> HtmlResponse:
        """
        Renderiza uma página de erro.
        """
        try:
            html = self._template_engine.render_template(
                self._error_template,
                status=status.value,
                message=message,
                model_name=self._model
            )
            return HtmlResponse(status, html)
        except Exception:
            # Fallback para HTML simples em caso de erro ao renderizar o template
            return HtmlResponse(
                status,
                f"<h1>Erro {status.value}</h1><p>{message}</p><a href='{self._base_route}'>Voltar</a>"
            )

    # Implementações das operações CRUD com templates

    def list_all_template(self, request: Request) -> HtmlResponse:
        """
        Lista todos os recursos em um template HTML.
        """
        items = self._dao.find_all()
        try:
            context = {
                f"{self._model.lower()}s": items,
                "title": f"Lista de {self._model}s",
                "base_route": self._base_route
            }
            html = self._template_engine.render_template(self._list_template, **context)
            return HtmlResponse(HttpStatus.OK, html)
        except Exception as e:
            return self._render_error(HttpStatus.INTERNAL_SERVER_ERROR, f"Erro ao renderizar template: {str(e)}")

    @Validator(id=int)
    def view_detail_template(self, request: Request, id) -> HtmlResponse:
        """
        Exibe os detalhes de um recurso em um template HTML.
        """
        item = self._dao.read(id)
        if not item:
            return self._render_error(HttpStatus.NOT_FOUND, f"{self._model} não encontrado")

        try:
            context = {
                self._model.lower(): item,
                "title": f"Detalhes do {self._model}",
                "base_route": self._base_route
            }
            html = self._template_engine.render_template(self._detail_template, **context)
            return HtmlResponse(HttpStatus.OK, html)
        except Exception as e:
            return self._render_error(HttpStatus.INTERNAL_SERVER_ERROR, f"Erro ao renderizar template: {str(e)}")

    def new_form_template(self, request: Request) -> HtmlResponse:
        """
        Exibe um formulário para criar um novo recurso.
        """
        try:
            # Obtém a classe do modelo para criar um objeto vazio (para campos do formulário)
            model_class = self._dao._model
            empty_item = model_class()

            context = {
                self._model.lower(): empty_item,
                "title": f"Novo {self._model}",
                "action": self._base_route,
                "method": "POST",
                "is_new": True,
                "base_route": self._base_route
            }
            html = self._template_engine.render_template(self._form_template, **context)
            return HtmlResponse(HttpStatus.OK, html)
        except Exception as e:
            return self._render_error(HttpStatus.INTERNAL_SERVER_ERROR, f"Erro ao renderizar formulário: {str(e)}")

    def create_from_form(self, request: Request) -> HtmlResponse:
        """
        Cria um novo recurso a partir dos dados do formulário.
        """
        data = request.form_data  # Presume que request possui acesso aos dados de formulário
        try:
            model_class = self._dao._model
            new_item = model_class(**data)
            saved_item = self._dao.save(new_item)

            # Redireciona para a página de detalhes do recurso criado
            return HtmlResponse(
                HttpStatus.SEE_OTHER,
                "",
                headers={"Location": f"{self._base_route}/{saved_item.id}"}
            )
        except Exception as e:
            # Em caso de erro, retorna ao formulário com a mensagem de erro
            context = {
                self._model.lower(): model_class(**data),
                "title": f"Novo {self._model}",
                "action": self._base_route,
                "method": "POST",
                "is_new": True,
                "error": str(e),
                "base_route": self._base_route
            }
            html = self._template_engine.render_template(self._form_template, **context)
            return HtmlResponse(HttpStatus.BAD_REQUEST, html)

    @Validator(id=int)
    def edit_form_template(self, request: Request, id) -> HtmlResponse:
        """
        Exibe um formulário para editar um recurso existente.
        """
        item = self._dao.read(id)
        if not item:
            return self._render_error(HttpStatus.NOT_FOUND, f"{self._model} não encontrado")

        try:
            context = {
                self._model.lower(): item,
                "title": f"Editar {self._model}",
                "action": f"{self._base_route}/{id}",
                "method": "POST",
                "is_new": False,
                "base_route": self._base_route
            }
            html = self._template_engine.render_template(self._form_template, **context)
            return HtmlResponse(HttpStatus.OK, html)
        except Exception as e:
            return self._render_error(HttpStatus.INTERNAL_SERVER_ERROR, f"Erro ao renderizar formulário: {str(e)}")

    @Validator(id=int)
    def update_from_form(self, request: Request, id) -> HtmlResponse:
        """
        Atualiza um recurso existente a partir dos dados do formulário.
        """
        data = request.form_data
        try:
            existing_item = self._dao.read(id)
            if not existing_item:
                return self._render_error(HttpStatus.NOT_FOUND, f"{self._model} não encontrado")

            # Atualiza os atributos
            for key, value in data.items():
                if hasattr(existing_item, key):
                    setattr(existing_item, key, value)

            # Salva as alterações
            self._dao.update(existing_item)

            # Redireciona para a página de detalhes
            return HtmlResponse(
                HttpStatus.SEE_OTHER,
                "",
                headers={"Location": f"{self._base_route}/{id}"}
            )
        except Exception as e:
            # Em caso de erro, retorna ao formulário com a mensagem de erro
            context = {
                self._model.lower(): existing_item,
                "title": f"Editar {self._model}",
                "action": f"{self._base_route}/{id}",
                "method": "POST",
                "is_new": False,
                "error": str(e),
                "base_route": self._base_route
            }
            html = self._template_engine.render_template(self._form_template, **context)
            return HtmlResponse(HttpStatus.BAD_REQUEST, html)

    @Validator(id=int)
    def delete_confirm_template(self, request: Request, id) -> HtmlResponse:
        """
        Exibe uma página de confirmação para excluir um recurso.
        """
        item = self._dao.read(id)
        if not item:
            return self._render_error(HttpStatus.NOT_FOUND, f"{self._model} não encontrado")

        try:
            # Presume que existe um template de confirmação de exclusão
            confirm_template = f"confirm_delete.html"
            context = {
                self._model.lower(): item,
                "title": f"Confirmar exclusão",
                "action": f"{self._base_route}/{id}/excluir",
                "method": "POST",
                "base_route": self._base_route
            }
            html = self._template_engine.render_template(confirm_template, **context)
            return HtmlResponse(HttpStatus.OK, html)
        except Exception as e:
            # Fallback para HTML simples em caso de erro ao renderizar o template
            html = f"""
            <h1>Confirmar exclusão</h1>
            <p>Tem certeza que deseja excluir {self._model} #{id}?</p>
            <form action="{self._base_route}/{id}/excluir" method="POST">
                <button type="submit">Confirmar</button>
                <a href="{self._base_route}/{id}">Cancelar</a>
            </form>
            """
            return HtmlResponse(HttpStatus.OK, html)

    @Validator(id=int)
    def delete_from_form(self, request: Request, id) -> HtmlResponse:
        """
        Exclui um recurso após confirmação.
        """
        try:
            existing_item = self._dao.read(id)
            if not existing_item:
                return self._render_error(HttpStatus.NOT_FOUND, f"{self._model} não encontrado")

            # Exclui o recurso
            self._dao.delete(id)

            # Redireciona para a lista
            return HtmlResponse(
                HttpStatus.SEE_OTHER,
                "",
                headers={"Location": f"{self._base_route}"}
            )
        except Exception as e:
            return self._render_error(
                HttpStatus.INTERNAL_SERVER_ERROR,
                f"Erro ao excluir {self._model}: {str(e)}"
            )


# Decorador para proteger rotas
def require_auth(redirect_to: str = "/login"):
    """
    Decorador para proteger rotas que exigem autenticação.
    Redireciona para a página de login se o usuário não estiver autenticado.

    Args:
        redirect_to: Rota para redirecionar se o usuário não estiver autenticado
    """
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapper(request: Request, *args, **kwargs):
            user = request.session.get("user")
            if not user:
                return RedirectResponse(redirect_to)
            return handler_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Decorador para proteção por perfil/role
def require_role(roles: List[str], redirect_to: str = "/unauthorized"):
    """
    Decorador para proteger rotas que exigem perfis específicos.
    Redireciona para uma página não autorizada se o usuário não tiver o perfil necessário.

    Args:
        roles: Lista de perfis permitidos
        redirect_to: Rota para redirecionar se o usuário não tiver permissão
    """
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapper(request: Request, *args, **kwargs):
            user = request.session.get("user")
            if not user:
                return RedirectResponse("/login")

            user_role = user.get("role", "user")  # Perfil padrão se não especificado

            if user_role not in roles:
                return RedirectResponse(redirect_to)

            return handler_func(request, *args, **kwargs)
        return wrapper
    return decorator


class AuthController(RestController):
    """
    Controlador genérico para autenticação.
    """
    _user_dao = None  # DAO para o modelo de usuário (deve ser definido pela subclasse)
    _login_template = "login.html"
    _register_template = "register.html"
    _unauthorized_template = "unauthorized.html"
    _enable_registration = True  # Define se o registro de usuários é permitido
    _username_field = "email"  # Campo usado como identificador de usuário
    _password_field = "senha"  # Campo usado como senha
    _redirect_after_login = "/dashboard"  # Rota para redirecionar após login bem-sucedido

    def __init__(self):
        if self._user_dao is None:
            raise NotImplementedError("A classe concreta deve definir o atributo _user_dao")

        # Não chama super().__init__() para evitar validação de DAO/Model da classe Controller
        from arcforge import template_engine  # Importação presumida
        self._template_engine = template_engine

        # Registra as rotas de autenticação
        self._register_auth_routes()

    def _register_auth_routes(self):
        """
        Registra as rotas de autenticação.
        """
        # Rotas de login
        Router.route("/login", "GET")(self.login_page)
        Router.route("/login", "POST")(self.login)

        # Rotas de logout
        Router.route("/logout", "GET")(self.logout)

        # Rotas de registro (opcional)
        if self._enable_registration:
            Router.route("/register", "GET")(self.register_page)
            Router.route("/register", "POST")(self.register)

        # Rota para página não autorizada
        Router.route("/unauthorized", "GET")(self.unauthorized_page)

    def login_page(self, request: Request) -> HtmlResponse:
        """
        Exibe a página de login.
        """
        context = {
            "title": "Login",
            "error": request.query_params.get("error")
        }
        html = self._template_engine.render_template(self._login_template, **context)
        return HtmlResponse(HttpStatus.OK, html)

    def login(self, request: Request) -> Response:
        """
        Processa a tentativa de login.
        """
        username = request.form_data.get(self._username_field)
        password = request.form_data.get(self._password_field)

        if not username or not password:
            return RedirectResponse("/login?error=Credenciais+incompletas")

        # Busca o usuário pelo campo de identificação (email, username, etc.)
        try:
            filter_params = {self._username_field: username}
            user = self._user_dao.find_one(**filter_params)

            if not user:
                logging.warning(f"Tentativa de login com {self._username_field} inexistente: {username}")
                return RedirectResponse("/login?error=Usuário+não+encontrado")

            # Valida a senha (deve ser implementado de forma segura com hash)
            if not self._validate_password(user, password):
                logging.warning(f"Senha incorreta para {username}")
                return RedirectResponse("/login?error=Senha+incorreta")

            # Constrói os dados do usuário para a sessão
            user_data = self._build_session_data(user)

            # Armazena na sessão
            request.session.set("user", user_data)

            logging.info(f"Login bem-sucedido: {username}")
            return RedirectResponse(self._redirect_after_login)

        except Exception as e:
            logging.error(f"Erro durante login: {str(e)}")
            return RedirectResponse("/login?error=Erro+interno")

    def logout(self, request: Request) -> Response:
        """
        Encerra a sessão do usuário.
        """
        request.session.clear()
        return RedirectResponse("/login")

    def register_page(self, request: Request) -> HtmlResponse:
        """
        Exibe a página de registro de usuário.
        """
        context = {
            "title": "Registro",
            "error": request.query_params.get("error")
        }
        html = self._template_engine.render_template(self._register_template, **context)
        return HtmlResponse(HttpStatus.OK, html)

    def register(self, request: Request) -> Response:
        """
        Processa o registro de um novo usuário.
        """
        # Implementação básica, deve ser sobrescrita para validações específicas
        try:
            # Extrai os dados do formulário
            user_data = request.form_data

            # Valida os dados antes de criar o usuário
            error = self._validate_registration_data(user_data)
            if error:
                return RedirectResponse(f"/register?error={error}")

            # Cria o novo usuário
            model_class = self._user_dao._model
            new_user = model_class(**user_data)

            # Se houver senha, deve ser hasheada antes de salvar
            if hasattr(new_user, self._password_field):
                password = getattr(new_user, self._password_field)
                hashed_password = self._hash_password(password)
                setattr(new_user, self._password_field, hashed_password)

            # Salva o novo usuário
            self._user_dao.save(new_user)

            logging.info(f"Novo usuário registrado: {getattr(new_user, self._username_field)}")
            return RedirectResponse("/login?msg=Registro+concluído")

        except Exception as e:
            logging.error(f"Erro durante registro: {str(e)}")
            return RedirectResponse("/register?error=Erro+interno")

    def unauthorized_page(self, request: Request) -> HtmlResponse:
        """
        Exibe a página de acesso não autorizado.
        """
        context = {
            "title": "Acesso Negado",
            "message": "Você não tem permissão para acessar este recurso."
        }
        try:
            html = self._template_engine.render_template(self._unauthorized_template, **context)
            return HtmlResponse(HttpStatus.FORBIDDEN, html)
        except Exception:
            html = """
            <h1>Acesso Negado</h1>
            <p>Você não tem permissão para acessar este recurso.</p>
            <a href="/login">Voltar para o login</a>
            """
            return HtmlResponse(HttpStatus.FORBIDDEN, html)

    # Métodos auxiliares que podem ser sobrescritos pelas subclasses

    def _validate_password(self, user, password: str) -> bool:
        """
        Valida a senha do usuário.
        Por padrão, faz uma comparação direta (não segura).
        Deve ser sobrescrito para usar hash de senhas em produção.
        """
        return getattr(user, self._password_field) == password

    def _hash_password(self, password: str) -> str:
        """
        Cria um hash da senha para armazenamento seguro.
        Por padrão, retorna a senha sem modificações (não seguro).
        Deve ser sobrescrito para usar hash de senhas em produção.
        """
        return password

    def _build_session_data(self, user) -> Dict[str, Any]:
        """
        Constrói os dados do usuário para armazenamento na sessão.
        Por padrão, inclui id, nome/username e email, se disponíveis.
        """
        data = {"id": user.id}

        # Adiciona campos comuns se existirem
        for field in ["nome", "username", "email", "role"]:
            if hasattr(user, field):
                data[field] = getattr(user, field)

        return data

    def _validate_registration_data(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Valida os dados de registro.
        Retorna uma mensagem de erro ou None se os dados forem válidos.
        """
        # Verifica se os campos obrigatórios estão presentes
        if self._username_field not in data or not data[self._username_field]:
            return f"O campo {self._username_field} é obrigatório"

        if self._password_field not in data or not data[self._password_field]:
            return "A senha é obrigatória"

        # Verifica se o usuário já existe
        filter_params = {self._username_field: data[self._username_field]}
        existing_user = self._user_dao.find_one(**filter_params)

        if existing_user:
            return f"Este {self._username_field} já está em uso"

        return None


# Versão protegida do Controller REST
class AuthenticatedController(RestController):
    """
    Versão do Controller que exige autenticação para todas as operações CRUD.
    """
    _require_auth = True  # Indica se a autenticação é necessária
    _auth_redirect = "/login"  # Rota para redirecionar se não autenticado
    _required_roles = None  # Perfis necessários para acessar este controller

    def _register_crud_routes(self):
        """
        Sobrescreve o método da classe pai para adicionar proteção de autenticação.
        """
        # Métodos protegidos
        for method_name, http_method, path_suffix in [
            ("list_all", "GET", ""),
            ("get_by_id", "GET", "/{id}"),
            ("create", "POST", ""),
            ("update", "PUT", "/{id}"),
            ("delete", "DELETE", "/{id}")
        ]:
            # Obtém o método original
            original_method = getattr(self, method_name)

            # Se autenticação for necessária, aplica o decorador
            if self._require_auth:
                # Aplicar decorador de autenticação
                protected_method = require_auth(self._auth_redirect)(original_method)

                # Se perfis específicos forem necessários, aplica o decorador de perfil
                if self._required_roles:
                    protected_method = require_role(self._required_roles)(protected_method)
            else:
                protected_method = original_method

            # Registra a rota com o método protegido
            path = f"{self._base_route}{path_suffix}"
            Router.route(path, http_method)(protected_method)


# Versão protegida do Controller de Template
class AuthenticatedTemplateController(TemplateController):
    """
    Versão do TemplateController que exige autenticação para todas as operações.
    """
    _require_auth = True  # Indica se a autenticação é necessária
    _auth_redirect = "/login"  # Rota para redirecionar se não autenticado
    _required_roles = None  # Perfis necessários para acessar este controller

    def _register_crud_routes(self):
        """
        Sobrescreve o método da classe pai para adicionar proteção de autenticação.
        """
        # Lista de métodos e suas rotas
        crud_routes = [
            ("list_all_template", "GET", ""),
            ("view_detail_template", "GET", "/{id}"),
            ("new_form_template", "GET", "/novo"),
            ("create_from_form", "POST", ""),
            ("edit_form_template", "GET", "/{id}/editar"),
            ("update_from_form", "POST", "/{id}"),
            ("delete_confirm_template", "GET", "/{id}/excluir"),
            ("delete_from_form", "POST", "/{id}/excluir")
        ]

        # Registra cada rota com proteção conforme necessário
        for method_name, http_method, path_suffix in crud_routes:
            # Obtém o método original
            original_method = getattr(self, method_name)

            # Se autenticação for necessária, aplica o decorador
            if self._require_auth:
                # Aplicar decorador de autenticação
                protected_method = require_auth(self._auth_redirect)(original_method)

                # Se perfis específicos forem necessários, aplica o decorador de perfil
                if self._required_roles:
                    protected_method = require_role(self._required_roles)(protected_method)
            else:
                protected_method = original_method

            # Registra a rota com o método protegido
            path = f"{self._base_route}{path_suffix}"
            Router.route(path, http_method)(protected_method)