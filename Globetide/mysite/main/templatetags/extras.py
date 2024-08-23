from django import template
from ..models import BlogComment

register = template.Library()

@register.filter
def get_index(h, i):
    try:
        value = h[int(i)]
    except:
        value = -1
    
    return value

@register.filter
def disp_login_data(dic, date):
    if date in dic:
        return dic[date]
    else:
        return 0
    
@register.filter
def get_num_comments(blog):
    return len(BlogComment.objects.filter(blog=blog))