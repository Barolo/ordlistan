# Ordlistan – Vocabulary Learning App (Flask)

Ordlistan är ett fullständigt webbaserat övningssystem för glosor med:
- användarkonton (login / register)
- personliga ordlistor
- import/export av listor
- delning av ordlistor
- smart quizmotor (viktad efter fel/rätt)
- statistikpanel
- responsivt UI
- e-postbaserad återställning av lösenord
- PostgreSQL i produktion, SQLite lokalt

Projektet är byggt på Flask med blueprint-struktur, migrations och modern frontend.

---

## 🚀 Teknisk översikt

### Backend
- Python 3.11+
- Flask
- Flask-Login
- Flask-Migrate
- SQLAlchemy
- PostgreSQL (Railway)
- SQLite lokalt

### Frontend
- Bootstrap 5.3
- Custom CSS
- FontAwesome
- Vanilla JS

---

## 📂 Projektstruktur

app/
└── init.py → Startar appen (create_app)
└── routes.py → Alla views, API-endpoints
└── models.py → Databastabeller
└── extensions.py → db, mail, migrate
└── templates/ → Jinja2 HTML-filer
└── static/ → CSS, bilder
migrations/ → DB-versioner
requirements.txt → Python-dependencies
Procfile → Railway/Gunicorn startkommando
.gitignore → Ignorerade filer


---

## 🧪 Köra lokalt

**1. Installera beroenden**


**2. Skapa `.env`**

SECRET_KEY=din_hemliga_nyckel
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_SUPPRESS_SEND=true


**3. Starta appen**

flask requirements


SQLite (`instance/site.db`) används automatiskt lokalt.

---

## 🌐 Deploy till Railway

1. Push till GitHub
2. Skapa ett nytt Railway-projekt
3. Välj “Deploy from GitHub”
4. Railway upptäcker Python automatiskt
5. Lägg in ENV-variabler:

SECRET_KEY=...
DATABASE_URL=postgresql://...
MAIL_USERNAME=...
MAIL_PASSWORD=...


6. Railway kör via Procfile:

web: gunicorn "app:create_app()"


Klart!

---

## ✨ Funktioner

- Skapa egna ordlistor
- Lägg till/ta bort/redigera ord
- Starta förhör från en eller flera listor
- Direktförhör från specifik lista
- Viktad slump (svåra ord dyker upp oftare)
- Resultathistorik
- Statistik i dashboard och profilsida
- Dela ordlistor med andra användare via e-post
- Admin-panel för superuser

---

## 👨‍💻 Utvecklad av
Rikard Nygander  
2025

---

# Slut på README
