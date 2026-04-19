import os
import markdown
from flask import Flask, render_template, abort
from config import CURSO, MODULOS, RAMAS_LATERALES, RECURSOS

app = Flask(__name__)

CONTENT_DIR = 'textos_md_kn_mk'

def load_md(mod_id):
    path = os.path.join(CONTENT_DIR, mod_id + '.md')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    return markdown.markdown(content, extensions=['extra', 'toc', 'tables'])

def get_modulo(mod_id):
    return next((m for m in MODULOS if m['id'] == mod_id), None)

@app.route('/')
def index():
    return render_template('index.html', curso=CURSO, modulos=MODULOS, recursos=RECURSOS)

@app.route('/modulo/<mod_id>')
def modulo(mod_id):
    m = get_modulo(mod_id)
    if not m:
        abort(404)
    idx   = MODULOS.index(m)
    prev_ = MODULOS[idx - 1] if idx > 0 else None
    next_ = MODULOS[idx + 1] if idx < len(MODULOS) - 1 else None
    html  = load_md(mod_id)
    return render_template('visor.html',
        curso=CURSO, m=m, modulos=MODULOS,
        ramas=RAMAS_LATERALES, prev=prev_, next=next_,
        content=html or markdown.markdown(m.get('texto', '')))

@app.route('/view/<path:filename>')
def view_file(filename):
    path = os.path.join(CONTENT_DIR, filename)
    if not os.path.exists(path):
        abort(404)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    html = markdown.markdown(content, extensions=['extra', 'toc', 'tables'])
    return render_template('visor.html',
        curso=CURSO, m={'titulo': filename, 'num': ''},
        modulos=MODULOS, ramas=RAMAS_LATERALES,
        prev=None, next=None, content=html)

@app.route('/recursos')
def recursos():
    return render_template('recursos.html',
        curso=CURSO,
        modulos=MODULOS,
        canal_youtube=RECURSOS['canal_youtube'])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
