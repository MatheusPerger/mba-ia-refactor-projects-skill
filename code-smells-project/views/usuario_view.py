def serializar_usuario(usuario):
    """Lista explícita de campos públicos: a senha nunca sai na resposta."""
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo": usuario.tipo,
        "criado_em": usuario.criado_em,
    }


def serializar_usuarios(usuarios):
    return [serializar_usuario(usuario) for usuario in usuarios]


def serializar_login(usuario, token):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo": usuario.tipo,
        "token": token,
    }
