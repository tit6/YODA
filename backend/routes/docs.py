from flask import Blueprint, render_template_string

docs_bp = Blueprint("docs", __name__)

SWAGGER_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>YODA API Docs</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.17.14/swagger-ui.min.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.17.14/swagger-ui-bundle.min.js"></script>
    <script>
      window.onload = function() {
        SwaggerUIBundle({
          url: "{{ spec_url }}",
          dom_id: '#swagger-ui',
          presets: [SwaggerUIBundle.presets.apis],
          layout: "BaseLayout"
        });
      };
    </script>
  </body>
</html>
"""


@docs_bp.route("/api/docs")
def swagger_ui():
    return render_template_string(SWAGGER_HTML, spec_url="/static/openapi.yaml")
