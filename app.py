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
    # Eliminar frontmatter YAML
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

@app.route('/recursos')
def recursos():
    # Lista todos los MD disponibles
    mds = []
    if os.path.exists(CONTENT_DIR):
        for f in sorted(os.listdir(CONTENT_DIR)):
            if f.endswith('.md'):
                mod_id = f.replace('.md', '')
                m = get_modulo(mod_id)
                mds.append({
                    'id': mod_id,
                    'titulo': m['titulo'] if m else mod_id,
                    'podcast_url': m.get('podcast_url', '') if m else ''
                })
    return render_template('recursos.html',
        curso=CURSO, mds=mds,
        canal_youtube=RECURSOS['canal_youtube'])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
