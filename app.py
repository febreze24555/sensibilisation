from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'phishing_secret_key'
DATABASE = 'inscriptions.db'

# Créneaux disponibles
CRENEAUX = [
    {'date': '12/05', 'heure': '11h-12h'},
    {'date': '15/05', 'heure': '11h-12h'},
    {'date': '19/05', 'heure': '11h-12h'},
    {'date': '22/05', 'heure': '11h-12h'},
    {'date': '26/05', 'heure': '11h-12h'},
    {'date': '29/05', 'heure': '11h-12h'},
]

# Initialisation de la base de données

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS inscriptions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nom TEXT,
                      prenom TEXT,
                      email TEXT,
                      service TEXT,
                      mode TEXT,
                      creneau TEXT)''')
        conn.commit()
        conn.close()
    else:
        # Migration si besoin (ajout email)
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        try:
            c.execute('ALTER TABLE inscriptions ADD COLUMN email TEXT')
            conn.commit()
        except:
            pass
        conn.close()

def hash_str(s):
    return hashlib.sha256(s.encode()).hexdigest()

ADMIN_LOGIN_HASH = hash_str('informatique@gruelfayer.fr')
ADMIN_PASSWORD_HASH = hash_str('Gruel123!')

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Récupérer le nombre d'inscrits par créneau
    inscrits = {}
    for creneau in CRENEAUX:
        c.execute("SELECT COUNT(*) FROM inscriptions WHERE creneau = ?", (creneau['date'],))
        inscrits[creneau['date']] = c.fetchone()[0]
    if request.method == 'POST':
        nom = request.form['nom'].strip()
        prenom = request.form['prenom'].strip()
        email = request.form['email'].strip()
        service = request.form['service'].strip()
        creneau = request.form['creneau']
        mode = request.form['mode']
        if inscrits[creneau] >= 10:
            flash('Ce créneau est déjà complet !')
        elif not nom or not prenom or not service:
            flash('Merci de remplir tous les champs.')
        else:
            c.execute('INSERT INTO inscriptions (nom, prenom, email, service, mode, creneau) VALUES (?, ?, ?, ?, ?, ?)',
                      (nom, prenom, email, service, mode, creneau))
            conn.commit()
            flash('Inscription réussie !')
            return redirect(url_for('index'))
    # Rafraîchir les inscrits après potentielle inscription
    inscrits = {}
    for creneau in CRENEAUX:
        c.execute("SELECT COUNT(*) FROM inscriptions WHERE creneau = ?", (creneau['date'],))
        inscrits[creneau['date']] = c.fetchone()[0]
    conn.close()
    return render_template('index.html', creneaux=CRENEAUX, inscrits=inscrits)

# --- ADMINISTRATION ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        if hash_str(login) == ADMIN_LOGIN_HASH and hash_str(password) == ADMIN_PASSWORD_HASH:
            session['admin_logged'] = True
            return redirect(url_for('admin'))
        else:
            error = "Identifiants invalides."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin_logged', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('admin_logged'):
        return redirect(url_for('login'))
    init_db()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    inscrits = {}
    for creneau in CRENEAUX:
        c.execute("SELECT * FROM inscriptions WHERE creneau = ? ORDER BY nom, prenom", (creneau['date'],))
        inscrits[creneau['date']] = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('admin.html', creneaux=CRENEAUX, inscrits=inscrits)

@app.route('/admin/edit/<int:inscrit_id>', methods=['GET', 'POST'])
def edit_inscrit(inscrit_id):
    init_db()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM inscriptions WHERE id = ?", (inscrit_id,))
    inscrit = c.fetchone()
    if not inscrit:
        conn.close()
        flash('Inscription introuvable.')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        nom = request.form['nom'].strip()
        prenom = request.form['prenom'].strip()
        email = request.form['email'].strip()
        service = request.form['service'].strip()
        creneau = request.form['creneau']
        mode = request.form['mode']
        c.execute("UPDATE inscriptions SET nom=?, prenom=?, email=?, service=?, creneau=?, mode=? WHERE id=?",
                  (nom, prenom, email, service, creneau, mode, inscrit_id))
        conn.commit()
        conn.close()
        flash('Inscription modifiée avec succès.')
        return redirect(url_for('admin'))
    inscrit = dict(inscrit)
    conn.close()
    return render_template('edit.html', inscrit=inscrit, creneaux=CRENEAUX)

@app.route('/admin/delete/<int:inscrit_id>')
def delete_inscrit(inscrit_id):
    init_db()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM inscriptions WHERE id = ?", (inscrit_id,))
    conn.commit()
    conn.close()
    flash('Inscription supprimée.')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
