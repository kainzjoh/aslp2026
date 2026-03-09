from flask import Flask, render_template_string, request, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "atemschutz-quiz-2024"

QUESTIONS = [
    {
        "id": 31,
        "category": "Atmung",
        "question": "Was ist Kohlenstoffmonoxid für ein Atemgift?",
        "options": ["a) Erstickend wirkendes Gift", "b) Blut und Nervengift", "c) Reiz- und Ätzgift"],
        "correct": "b"
    },
    {
        "id": 32,
        "category": "Atmung",
        "question": "Wie kann man Sauerstoffmangel in der Umgebungsluft erkennen?",
        "options": ["a) Nur mit speziellen Messgeräten", "b) An der blauen Färbung der Luft", "c) Durch Kerzen Schnelltests"],
        "correct": "a"
    },
    {
        "id": 33,
        "category": "Atmung",
        "question": "Woran erkennt man eine gesunde Atemtechnik?",
        "options": ["a) Am ruhigen Ein- und Ausatmen", "b) An der langsamen Brustatmung", "c) An der beständigen, pausenlosen Atmung unter Beachtung der Atemgymnastik"],
        "correct": "a"
    },
    {
        "id": 34,
        "category": "Atmung",
        "question": "Welche Folge kann eine gestörte Atmung (Atemkrise) hervorrufen?",
        "options": ["a) Rauschzustände", "b) Lebensgefahr", "c) Depressionen"],
        "correct": "b"
    },
    {
        "id": 35,
        "category": "Atmung",
        "question": "Was geschieht mit der Atemluft in der Lunge?",
        "options": [
            "a) Teile des Stickstoffes werden vom Blut aufgenommen, Kohlendioxid abtransportiert",
            "b) Sauerstoff wird vom Blut aufgenommen, Kohlenstoffdioxid vom Blut in die Lunge (Gasaustausch) abgegeben",
            "c) Kohlendioxid (CO2) wird an das Blut übertragen, um das Atemzentrum anzuregen"
        ],
        "correct": "b"
    },
    {
        "id": 36,
        "category": "Atmung",
        "question": "In welcher Form können atemschädliche Stoffe in der Luft vorkommen?",
        "options": ["a) Nur gasförmig", "b) Als Partikel, Gase und Dämpfe", "c) Nur in Kombination mit Aerosolen"],
        "correct": "b"
    },
    {
        "id": 37,
        "category": "Atmung",
        "question": "Wann muss ein Atemschutzgeräteträger zur ärztlichen Nachuntersuchung (AKL-Test)?",
        "options": [
            "a) Jährlich",
            "b) Bis zum 40. Lebensjahr alle 5 Jahre, zwischen 40. und 50. Lebensjahr alle 3 Jahre, ab dem 50. Lebensjahr alle 2 Jahre oder nach schwerer Erkrankung",
            "c) Alle 3 Jahre bis zum 40. Lebensjahr, alle 2 Jahre bis zum 60. Lebensjahr, danach jährlich"
        ],
        "correct": "b"
    },
    {
        "id": 38,
        "category": "Atmung",
        "question": "Wie kann man einer Atemkrise entgegenwirken?",
        "options": [
            "a) Durch schnelle Atemzüge",
            "b) Durch ruhiges, tiefes Ein- und Ausatmen",
            "c) Durch Drücken des Zuschussknopfes am Lungenautomaten"
        ],
        "correct": "b"
    },
    {
        "id": 39,
        "category": "Atmung",
        "question": "Wie viel Luft veratmet ein AGT durchschnittlich bei einem Atemschutzeinsatz?",
        "options": ["a) 20 – 30 Liter/min", "b) 60 – 90 Liter/min", "c) 40 – 50 Liter/min"],
        "correct": "c"
    },
    {
        "id": 40,
        "category": "Gerätekunde",
        "question": "Was hat auf jedem Pressluftatmer (PA) zumindest montiert zu sein?",
        "options": ["a) Ein Notsignalgeber", "b) Keile und Bandschlingen", "c) Ein Haltegurt mit zusätzlichen Karabinern"],
        "correct": "a"
    },
    {
        "id": 41,
        "category": "Gerätekunde",
        "question": "Warum werden bei der Feuerwehr Kombinationsfilter verwendet?",
        "options": [
            "a) Weil er in Kombination mit der Atemschutzmaske Schutz vor mehreren Gasen bietet",
            "b) Damit ein Schutz vor Gasen und Partikeln gegeben ist",
            "c) Kombinationsfilter sind mit allen Masken kompatibel"
        ],
        "correct": "b"
    },
    {
        "id": 42,
        "category": "Gerätekunde",
        "question": "Schützen Filtergeräte gegen Sauerstoffmangel?",
        "options": ["a) Ja", "b) Bedingt", "c) Nein"],
        "correct": "c"
    },
    {
        "id": 43,
        "category": "Gerätekunde",
        "question": "Wogegen schützt die Brandfluchthaube?",
        "options": [
            "a) Gegen Brandrauch ausschließlich Kohlenstoffmonoxid",
            "b) Nur gegen Kohlenstoffmonoxid",
            "c) Kurzzeitig gegen verschiedene Atemgifte einschließlich Kohlenstoffmonoxid"
        ],
        "correct": "c"
    },
    {
        "id": 44,
        "category": "Gerätekunde",
        "question": "Welcher Bauteil der Atemmaske sorgt für die Sprechverbindung nach außen?",
        "options": ["a) Die Sprechmembrane", "b) Das Mikrofon bei Funkmasken", "c) Der Hohlraum in der Innenmaske"],
        "correct": "a"
    },
    {
        "id": 45,
        "category": "Gerätekunde",
        "question": "Welches Ventil ist für die Dichtheit der Maske besonders wichtig?",
        "options": ["a) Das Einatemventil", "b) Das Ausatemventil", "c) Das Steuerventil"],
        "correct": "b"
    },
    {
        "id": 46,
        "category": "Gerätekunde",
        "question": "Wer führt die Pflege der Atemmasken nach der Verwendung durch?",
        "options": [
            "a) Der Atemschutzwart mit Unterstützung der Geräteträger",
            "b) Der Geräteträger",
            "c) Der Gerätemeister, der Atemschutzwart überwacht und prüft"
        ],
        "correct": "a"
    },
    {
        "id": 47,
        "category": "Gerätekunde",
        "question": "Warum sind Atemmasken mit einer Innenmaske ausgestattet?",
        "options": [
            "a) Zur Erleichterung der Wartung",
            "b) Um eine angenehme Luftführung zu erreichen",
            "c) Verkleinerung des Totraumes, das Beschlagen der Sichtscheibe wird weitgehend verhindert"
        ],
        "correct": "c"
    },
    {
        "id": 48,
        "category": "Gerätekunde",
        "question": "Wie viele AS-Trupps können mit einem Außenüberwachungsgerät (Modell Steiermark) zeitgleich überwacht werden?",
        "options": ["a) Zwei", "b) Drei", "c) Vier"],
        "correct": "b"
    },
    {
        "id": 49,
        "category": "Gerätekunde",
        "question": "Welche Funktion hat der Lungenautomat?",
        "options": [
            "a) Abgabe der Atemluft an den Atemschutzgeräteträger entsprechend seines Bedarfs",
            "b) Er verringert den Widerstand beim Atmen",
            "c) Er reduziert den Luftdruck von Hochdruck auf Niederdruck"
        ],
        "correct": "a"
    },
    {
        "id": 50,
        "category": "Gerätekunde",
        "question": "Darf mit einem Pressluftatmer getaucht werden?",
        "options": ["a) Nur bis fünf Meter", "b) Nein", "c) Ja, aber nur mit Tauchmaske"],
        "correct": "b"
    },
    {
        "id": 51,
        "category": "Gerätekunde",
        "question": "Wer darf defekte Atemschutzgeräte und Atemmasken reparieren?",
        "options": [
            "a) Die Hersteller und autorisierte Atemschutzwerkstätten (z.B.: LFV Steiermark)",
            "b) Der Atemschutzwart der Feuerwehr",
            "c) Jeder mit Atemschutzgeräteträger Lehrgang"
        ],
        "correct": "a"
    },
    {
        "id": 52,
        "category": "Gerätekunde",
        "question": "Welches Volumen / Druck können Pressluftflaschen für Atemschutzgeräte haben?",
        "options": [
            "a) 4 Liter / 200 bar; 6 Liter / 300 bar; 6,8 Liter / 300 bar",
            "b) 2 Liter / 300 bar; 4 Liter / 300 bar; 15 Liter / 200 bar",
            "c) 6,8 Liter / 200 bar; 6 Liter / 200 bar; 4 Liter / 300 bar"
        ],
        "correct": "a"
    },
    {
        "id": 53,
        "category": "Allgemeine Fragen",
        "question": "Kann ein (Voll)Bartträger als Atemschutzgeräteträger eingesetzt werden?",
        "options": [
            "a) Ja, mit Überdruckmaske",
            "b) Es ist egal ob man einen Vollbart hat",
            "c) Nein, der dichte Sitz der Atemmaske ist nicht mehr gewährleistet"
        ],
        "correct": "c"
    },
    {
        "id": 54,
        "category": "Allgemeine Fragen",
        "question": "Im Trupp löst ein Notsignalgeber aus. Was ist sofort zu tun?",
        "options": [
            "a) Einsatzauftrag abschließen, danach sich um das Signal kümmern",
            "b) Einsatzauftrag abbrechen, Kontakt mit dem Truppmitglied aufnehmen, Hilfe leisten",
            "c) Trupp teilen, ein Mitglied kümmert sich um das Notsignal, das andere setzt den Einsatzauftrag fort"
        ],
        "correct": "b"
    },
    {
        "id": 55,
        "category": "Allgemeine Fragen",
        "question": "Wann muss der GK als Außenüberwacher mit dem Atemschutztrupp Funkkontakt aufnehmen?",
        "options": [
            "a) Alle 5 Minuten um den Flaschendruck zu kontrollieren",
            "b) Bei Einsatzbeginn (Funkprobe); gegebenenfalls bei 20, immer bei 10, und 0 Minuten Resteinsatzzeit",
            "c) Bei Einsatzbeginn und bei Einsatzende"
        ],
        "correct": "b"
    },
    {
        "id": 56,
        "category": "Allgemeine Fragen",
        "question": "Wer trägt für die Außenüberwachung des AS-Trupps die Verantwortung?",
        "options": [
            "a) Der Gruppenkommandant",
            "b) Der Leiter des Atemschutzsammelplatzes",
            "c) Der Atemschutzbeauftragte der Feuerwehr"
        ],
        "correct": "a"
    },
    {
        "id": 57,
        "category": "Allgemeine Fragen",
        "question": "Mindestalter für Atemschutzgeräteträger?",
        "options": [
            "a) 20 Jahre ohne Grundausbildung",
            "b) 16 Jahre mit Grundausbildung",
            "c) Vollendetes 18. Lebensjahr"
        ],
        "correct": "c"
    },
    {
        "id": 58,
        "category": "Allgemeine Fragen",
        "question": "Was ist vor Beendigung des Atemschutzeinsatzes (z.B. Brandeinsatz) zu beachten?",
        "options": [
            "a) Alarmierung des Atemschutzbereichsbeauftragten",
            "b) Organisation von Speisen, Getränken und Rauchwaren",
            "c) Eine Grobdekontamination ist noch am Einsatzort durchzuführen"
        ],
        "correct": "c"
    },
    {
        "id": 59,
        "category": "Allgemeine Fragen",
        "question": "Warum soll jedes mit Atemschutz ausgestattete Feuerwehrfahrzeug mit einem Außenüberwachungsgerät ausgestattet sein?",
        "options": [
            "a) Damit jeder Atemschutztrupp von Beginn des Einsatzes an überwacht werden kann",
            "b) Damit ausreichend Reservegeräte vorhanden sind",
            "c) Damit eine Funkverbindung zu den eingesetzten Atemschutztrupps aufgebaut werden kann"
        ],
        "correct": "a"
    },
    {
        "id": 60,
        "category": "Allgemeine Fragen",
        "question": "Wann hat ein in Bereitschaft stehender AS-Rettungstrupp die Atemmaske nicht aufgesetzt?",
        "options": [
            "a) Wenn sich nur ein Angriffstrupp im Gefahrenbereich befindet",
            "b) Wenn durch die Witterung oder die Technik der Atemmaske die Sichtscheibe innen beschlägt",
            "c) Wenn eine Lagerung in der Maskendose möglich ist"
        ],
        "correct": "b"
    },
]

TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Atemschutz Leistungsprüfung – Training</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1rem;
    }

    .container {
      width: 100%;
      max-width: 720px;
    }

    header {
      text-align: center;
      margin-bottom: 2rem;
    }

    header h1 {
      font-size: 1.4rem;
      font-weight: 700;
      color: #f97316;
      letter-spacing: 0.02em;
    }

    header p {
      font-size: 0.85rem;
      color: #64748b;
      margin-top: 0.3rem;
    }

    /* Progress bar */
    .progress-wrap {
      background: #1e2433;
      border-radius: 99px;
      height: 6px;
      margin-bottom: 1.5rem;
      overflow: hidden;
    }
    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #f97316, #fb923c);
      border-radius: 99px;
      transition: width 0.4s ease;
    }
    .progress-label {
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      color: #475569;
      margin-bottom: 0.5rem;
    }

    /* Card */
    .card {
      background: #1a2035;
      border: 1px solid #2d3748;
      border-radius: 14px;
      padding: 1.8rem 2rem;
      margin-bottom: 1.2rem;
    }

    .category-badge {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #f97316;
      background: rgba(249,115,22,0.12);
      border: 1px solid rgba(249,115,22,0.25);
      border-radius: 99px;
      padding: 0.2rem 0.75rem;
      margin-bottom: 1rem;
    }

    .question-num {
      font-size: 0.8rem;
      color: #475569;
      margin-bottom: 0.4rem;
    }

    .question-text {
      font-size: 1.05rem;
      font-weight: 600;
      line-height: 1.5;
      color: #f1f5f9;
      margin-bottom: 1.4rem;
    }

    /* Options */
    .options { display: flex; flex-direction: column; gap: 0.65rem; }

    .option {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      background: #0f1117;
      border: 1px solid #2d3748;
      border-radius: 10px;
      padding: 0.85rem 1rem;
      cursor: pointer;
      transition: border-color 0.15s, background 0.15s;
      text-align: left;
      font-size: 0.92rem;
      color: #cbd5e1;
      line-height: 1.45;
      width: 100%;
    }

    .option:hover:not(:disabled) {
      border-color: #f97316;
      background: rgba(249,115,22,0.06);
      color: #f1f5f9;
    }

    .option .key {
      font-weight: 700;
      color: #94a3b8;
      min-width: 1.2rem;
      flex-shrink: 0;
    }

    .option.correct {
      border-color: #22c55e !important;
      background: rgba(34,197,94,0.08) !important;
      color: #86efac !important;
    }
    .option.correct .key { color: #22c55e; }

    .option.wrong {
      border-color: #ef4444 !important;
      background: rgba(239,68,68,0.08) !important;
      color: #fca5a5 !important;
    }
    .option.wrong .key { color: #ef4444; }

    .option:disabled { cursor: default; }

    /* Feedback */
    .feedback {
      margin-top: 1rem;
      font-size: 0.88rem;
      padding: 0.65rem 1rem;
      border-radius: 8px;
      display: none;
    }
    .feedback.show { display: block; }
    .feedback.ok  { background: rgba(34,197,94,0.1);  color: #86efac; border: 1px solid rgba(34,197,94,0.25); }
    .feedback.err { background: rgba(239,68,68,0.1);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.25); }

    /* Buttons */
    .btn {
      display: inline-block;
      padding: 0.7rem 1.6rem;
      border-radius: 10px;
      border: none;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.15s, transform 0.1s;
    }
    .btn:active { transform: scale(0.97); }
    .btn-primary { background: #f97316; color: #fff; }
    .btn-primary:hover { opacity: 0.9; }
    .btn-ghost { background: #1e2433; color: #94a3b8; border: 1px solid #2d3748; }
    .btn-ghost:hover { border-color: #475569; color: #cbd5e1; }

    .nav-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 1.2rem;
      gap: 1rem;
    }

    /* Result screen */
    .result-card {
      text-align: center;
      padding: 2.5rem;
    }

    .result-score {
      font-size: 4rem;
      font-weight: 800;
      color: #f97316;
      line-height: 1;
      margin-bottom: 0.5rem;
    }

    .result-sub {
      font-size: 1rem;
      color: #64748b;
      margin-bottom: 1.5rem;
    }

    .result-verdict {
      font-size: 1.1rem;
      font-weight: 600;
      padding: 0.6rem 1.4rem;
      border-radius: 99px;
      display: inline-block;
      margin-bottom: 2rem;
    }
    .verdict-pass { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
    .verdict-fail { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

    .category-stats {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-bottom: 2rem;
      text-align: left;
    }
    .cat-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #0f1117;
      border: 1px solid #2d3748;
      border-radius: 8px;
      padding: 0.6rem 1rem;
      font-size: 0.88rem;
    }
    .cat-row .cat-name { color: #94a3b8; }
    .cat-row .cat-score { font-weight: 700; color: #f1f5f9; }

    /* Start screen */
    .start-card { text-align: center; padding: 2.5rem; }
    .start-icon { font-size: 3rem; margin-bottom: 1rem; }
    .start-card h2 { font-size: 1.3rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.5rem; }
    .start-card p  { color: #64748b; font-size: 0.9rem; margin-bottom: 1.5rem; line-height: 1.6; }

    .mode-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
    }
    .mode-btn {
      background: #0f1117;
      border: 1px solid #2d3748;
      border-radius: 10px;
      padding: 1rem;
      cursor: pointer;
      text-align: center;
      transition: border-color 0.15s, background 0.15s;
      text-decoration: none;
      display: block;
    }
    .mode-btn:hover { border-color: #f97316; background: rgba(249,115,22,0.06); }
    .mode-btn .mode-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
    .mode-btn .mode-label { font-size: 0.85rem; font-weight: 600; color: #f1f5f9; }
    .mode-btn .mode-desc { font-size: 0.75rem; color: #475569; margin-top: 0.2rem; }

    @media(max-width: 480px) {
      .card { padding: 1.2rem; }
      .mode-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
<div class="container">
  <header>
    <h1>🔥 Atemschutz Leistungsprüfung</h1>
    <p>Stufe 2 – Trainingsquiz</p>
  </header>

  {% block content %}{% endblock %}
</div>

<script>
  // Highlight selected option, disable others, show feedback, then reveal next button
  document.querySelectorAll('.option').forEach(btn => {
    btn.addEventListener('click', function() {
      const correct = this.dataset.correct === 'true';
      const allOpts = document.querySelectorAll('.option');
      allOpts.forEach(b => {
        b.disabled = true;
        if (b.dataset.correct === 'true') b.classList.add('correct');
      });
      if (!correct) this.classList.add('wrong');
      const fb = document.getElementById('feedback');
      if (fb) {
        fb.classList.add('show', correct ? 'ok' : 'err');
        fb.textContent = correct ? '✓ Richtig!' : '✗ Falsch – die richtige Antwort ist grün markiert.';
      }
      document.getElementById('next-btn').style.display = 'inline-block';
      document.getElementById('skip-btn') && (document.getElementById('skip-btn').style.display = 'none');
      // Auto-submit after small delay so the user sees the result
      // (manual click still required)
    });
  });
</script>
</body>
</html>
"""

QUESTION_TEMPLATE = TEMPLATE.replace("{% block content %}{% endblock %}", """
{% block content %}
<div class="progress-label">
  <span>Frage {{ current + 1 }} von {{ total }}</span>
  <span>{{ score }} richtig</span>
</div>
<div class="progress-wrap">
  <div class="progress-bar" style="width: {{ ((current) / total * 100)|int }}%"></div>
</div>

<div class="card">
  <span class="category-badge">{{ q.category }}</span>
  <div class="question-num">Frage {{ q.id }}</div>
  <div class="question-text">{{ q.question }}</div>
  <div class="options">
    {% for opt in q.options %}
      {% set letter = ['a','b','c'][loop.index0] %}
      <button class="option"
              data-correct="{{ 'true' if letter == q.correct else 'false' }}"
              data-value="{{ letter }}">
        <span class="key">{{ letter }})</span>
        <span>{{ opt[3:] }}</span>
      </button>
    {% endfor %}
  </div>
  <div class="feedback" id="feedback"></div>
</div>

<form method="post" action="/answer" id="answer-form">
  <input type="hidden" name="answer" id="answer-input" value="">
  <div class="nav-row">
    <a href="/restart" class="btn btn-ghost">↩ Neu starten</a>
    <div style="display:flex; gap:0.6rem;">
      <button type="button" id="skip-btn" class="btn btn-ghost" onclick="submitAnswer('skip')">Überspringen</button>
      <button type="button" id="next-btn" class="btn btn-primary" style="display:none" onclick="submitAnswer('')">Weiter →</button>
    </div>
  </div>
</form>

<script>
  document.querySelectorAll('.option').forEach(btn => {
    btn.addEventListener('click', function() {
      document.getElementById('answer-input').value = this.dataset.value;
    });
  });
  function submitAnswer(val) {
    if (val === 'skip') document.getElementById('answer-input').value = 'skip';
    document.getElementById('answer-form').submit();
  }
</script>
{% endblock %}
""")

RESULT_TEMPLATE = TEMPLATE.replace("{% block content %}{% endblock %}", """
{% block content %}
<div class="card result-card">
  <div class="result-score">{{ score }}/{{ total }}</div>
  <div class="result-sub">{{ pct }}% korrekt beantwortet</div>
  <div class="result-verdict {{ 'verdict-pass' if pct >= 75 else 'verdict-fail' }}">
    {{ '🎉 Bestanden!' if pct >= 75 else '❌ Nicht bestanden – weiterüben!' }}
  </div>

  <div class="category-stats">
    {% for cat, data in cats.items() %}
    <div class="cat-row">
      <span class="cat-name">{{ cat }}</span>
      <span class="cat-score">{{ data.score }}/{{ data.total }}</span>
    </div>
    {% endfor %}
  </div>

  <div style="display:flex; gap:0.75rem; justify-content:center; flex-wrap:wrap;">
    <a href="/restart" class="btn btn-primary">🔄 Nochmal versuchen</a>
    <a href="/restart?shuffle=1" class="btn btn-ghost">🔀 Zufällige Reihenfolge</a>
    <a href="/review" class="btn btn-ghost">📋 Alle Fragen & Antworten</a>
  </div>
</div>
{% endblock %}
""")

START_TEMPLATE = TEMPLATE.replace("{% block content %}{% endblock %}", """
{% block content %}
<div class="card start-card">
  <div class="start-icon">🧰</div>
  <h2>Atemschutz Trainingsquiz</h2>
  <p>{{ total }} Fragen aus den Kategorien Atmung, Gerätekunde und Allgemeine Fragen.<br>Wähle einen Modus und starte.</p>

  <div class="mode-grid">
    <a href="/start?mode=all" class="mode-btn">
      <div class="mode-icon">📚</div>
      <div class="mode-label">Alle Fragen</div>
      <div class="mode-desc">In Reihenfolge</div>
    </a>
    <a href="/start?mode=shuffle" class="mode-btn">
      <div class="mode-icon">🔀</div>
      <div class="mode-label">Zufällig</div>
      <div class="mode-desc">Gemischt</div>
    </a>
    <a href="/start?mode=atmung" class="mode-btn">
      <div class="mode-icon">🫁</div>
      <div class="mode-label">Nur Atmung</div>
      <div class="mode-desc">Fragen 31–39</div>
    </a>
    <a href="/start?mode=geraet" class="mode-btn">
      <div class="mode-icon">🔧</div>
      <div class="mode-label">Nur Gerätekunde</div>
      <div class="mode-desc">Fragen 40–52</div>
    </a>
  </div>
</div>
{% endblock %}
""")

REVIEW_TEMPLATE = TEMPLATE.replace("{% block content %}{% endblock %}", """
{% block content %}
<div style="margin-bottom:1rem; display:flex; justify-content:space-between; align-items:center;">
  <h2 style="font-size:1rem; color:#94a3b8;">Alle Fragen & richtige Antworten</h2>
  <a href="/" class="btn btn-ghost" style="padding:0.4rem 0.9rem; font-size:0.85rem;">← Zurück</a>
</div>
{% for q in questions %}
<div class="card" style="margin-bottom:0.75rem; padding:1.2rem 1.4rem;">
  <span class="category-badge">{{ q.category }}</span>
  <div class="question-num">Frage {{ q.id }}</div>
  <div class="question-text" style="font-size:0.95rem; margin-bottom:0.8rem;">{{ q.question }}</div>
  <div class="options">
    {% for opt in q.options %}
      {% set letter = ['a','b','c'][loop.index0] %}
      <div class="option {{ 'correct' if letter == q.correct else '' }}" style="cursor:default; padding:0.65rem 0.9rem;">
        <span class="key">{{ letter }})</span>
        <span style="font-size:0.88rem;">{{ opt[3:] }}</span>
      </div>
    {% endfor %}
  </div>
</div>
{% endfor %}
{% endblock %}
""")


@app.route("/")
def index():
    return render_template_string(START_TEMPLATE, total=len(QUESTIONS))

@app.route("/start")
def start():
    mode = request.args.get("mode", "all")
    qs = QUESTIONS.copy()
    if mode == "shuffle":
        random.shuffle(qs)
    elif mode == "atmung":
        qs = [q for q in qs if q["category"] == "Atmung"]
    elif mode == "geraet":
        qs = [q for q in qs if q["category"] == "Gerätekunde"]
    session["questions"] = qs
    session["index"] = 0
    session["score"] = 0
    session["answers"] = []
    return redirect(url_for("quiz"))

@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))

@app.route("/quiz")
def quiz():
    qs = session.get("questions", [])
    idx = session.get("index", 0)
    if idx >= len(qs):
        return redirect(url_for("result"))
    q = qs[idx]
    return render_template_string(
        QUESTION_TEMPLATE,
        q=q,
        current=idx,
        total=len(qs),
        score=session.get("score", 0)
    )

@app.route("/answer", methods=["POST"])
def answer():
    qs = session.get("questions", [])
    idx = session.get("index", 0)
    if idx < len(qs):
        ans = request.form.get("answer", "skip")
        q = qs[idx]
        if ans == q["correct"]:
            session["score"] = session.get("score", 0) + 1
        session["answers"] = session.get("answers", []) + [ans]
        session["index"] = idx + 1
    return redirect(url_for("quiz"))

@app.route("/result")
def result():
    qs = session.get("questions", [])
    score = session.get("score", 0)
    total = len(qs)
    pct = int(score / total * 100) if total else 0

    cats = {}
    answers = session.get("answers", [])
    for i, q in enumerate(qs):
        c = q["category"]
        if c not in cats:
            cats[c] = {"score": 0, "total": 0}
        cats[c]["total"] += 1
        if i < len(answers) and answers[i] == q["correct"]:
            cats[c]["score"] += 1

    return render_template_string(RESULT_TEMPLATE, score=score, total=total, pct=pct, cats=cats)

@app.route("/review")
def review():
    return render_template_string(REVIEW_TEMPLATE, questions=QUESTIONS)

if __name__ == "__main__":
    app.run(debug=True, port=5000)