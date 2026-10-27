def user_to_dict(user):
    """Campos públicos do usuário; o hash da senha nunca sai."""
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'active': user.active,
        'created_at': str(user.created_at),
    }


def user_list_item(user, task_count):
    return {**user_to_dict(user), 'task_count': task_count}
