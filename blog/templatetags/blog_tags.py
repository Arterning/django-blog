from django import template

register = template.Library()


@register.filter
def split_tags(value, delimiter=','):
    """
    将标签字符串分割为列表
    使用方法: {{ post.tags|split_tags }}
    """
    if not value:
        return []
    return [tag.strip() for tag in value.split(delimiter) if tag.strip()]
