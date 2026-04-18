import os
import markdown as md_lib
from flask import Flask, render_template, abort
from config import CURSO, MODULOS, RAMAS_LATERALES

app = Flask(__name__)

def get_modulo(mod_id):
    return next((m for m in MODULOS if m['id'] == mod_id), None)

def load_md_content(mod_id):
    path = os.path.join('contenido', f'{mod_id}.md')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    # Strip YAML frontmatter
    if raw.startswith('---'):
        parts = raw.split('---', 2)
        if len(parts) >= 3:
            raw = parts[2].lstrip('\n')
    return md_lib.markdown(raw, extensions=['extra', 'toc'])

@app.route('/')
def index():
    return render_template('index.html', curso=CURSO, modulos=MODULOS)

@app.route('/modulo/<mod_id>')
def modulo(mod_id):
    m = get_modulo(mod_id)
    if not m:
        abort(404)
    html_content = load_md_content(mod_id)
    if html_content is None:
        html_content = md_lib.markdown(m['texto'])
    idx   = MODULOS.index(m)
    prev_ = MODULOS[idx - 1] if idx > 0 else None
    next_ = MODULOS[idx + 1] if idx < len(MODULOS) - 1 else None
    return render_template('visor.html',
        title=m['titulo'],
        content=html_content,
        prev=prev_, next=next_)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
