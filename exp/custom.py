# this file imports custom routes into the experiment server
from flask import (
    abort,
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    Response
)


# There are no custom code routes in this experiment. psiTurk just
# expects this to exist and the experiment server will fail to start
# without it
custom_code = Blueprint('custom_code',
                        __name__,
                        template_folder='templates',
                        static_folder='static')
