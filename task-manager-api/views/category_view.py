def category_to_dict(category):
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'created_at': str(category.created_at),
    }


def category_list_item(category, task_count):
    return {**category_to_dict(category), 'task_count': task_count}
