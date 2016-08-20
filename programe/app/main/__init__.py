from flask import Blueprint
from datetime import datetime
main = Blueprint('main', __name__)
Now = datetime.now()
from . import views, errors
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission, Now=Now)
