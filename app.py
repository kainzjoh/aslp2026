"""
Atemschutz Leistungsprüfung – Trainingsquiz
Fix: session only stores small indices, never full question objects.
      This avoids Flask cookie overflow (4 KB limit) which silently
      wiped the Bronze session and caused instant redirect to result.
"""
from flask import Flask, render_template_string, request, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "atemschutz-quiz-2024"

# ── BRONZE – Stufe 1 ──────────────────────────────────────────────────────────
QUESTIONS_BRONZE = [
    {"id":1,"level":"bronze","category":"Atmung",
     "question":"Woraus setzt sich die Umgebungsluft (Einatemluft) zusammen?",
     "options":["a) 17% Sauerstoff, 78% Stickstoff, 4,00% Kohlenstoffdioxid, 1,00% Edelgas",
                "b) 21% Sauerstoff, 78% Stickstoff, 0,04% Kohlenstoffdioxid, 0,96% Edelgase",
                "c) 21% Stickstoff, 78% Sauerstoff, 0,04% Kohlenstoffdioxid, 0,96% Edelgase"],"correct":"b"},
    {"id":2,"level":"bronze","category":"Atmung",
     "question":"Wie kann eine Atemkrise ausgelöst werden?",
     "options":["a) Durch eine falsche Atemtechnik (z.B. durch flaches, hastiges Atmen) bzw. Sauerstoffmangel",
                "b) Gar nicht",
                "c) Durch zu viel Feuchtigkeit in der Atemluft"],"correct":"a"},
    {"id":3,"level":"bronze","category":"Atmung",
     "question":"Wie lange kann ein Mensch ohne Sauerstoff (Atmung), ohne Schäden zu bekommen, auskommen?",
     "options":["a) ca. 3 Minuten","b) ca. 5 Minuten","c) ca. 1,5 Minuten"],"correct":"a"},
    {"id":4,"level":"bronze","category":"Atmung",
     "question":"Aus welchen Bestandteilen setzt sich die ausgeatmete Atemluft zusammen?",
     "options":["a) 14% Sauerstoff, 81% Stickstoff, 4,00% Edelgase, 1% Kohlenstoffdioxid",
                "b) 20% Sauerstoff, 79% Kohlenstoffdioxid, 1% Stickstoff",
                "c) 17% Sauerstoff, 78% Stickstoff, 4,04% Kohlenstoffdioxid, 0,96% Edelgase"],"correct":"c"},
    {"id":5,"level":"bronze","category":"Atmung",
     "question":"Welches Atemgift wirkt nur auf die äußere Atmung?",
     "options":["a) Kohlenstoffdioxid (CO₂)","b) Kohlenstoffmonoxid (CO)","c) Blausäuredämpfe (HCN)"],"correct":"a"},
    {"id":6,"level":"bronze","category":"Gerätekunde",
     "question":"Was sind Atemschutzgeräte?",
     "options":["a) Geräte, mit welchen man sich vor heißer Einatemluft schützt",
                "b) Geräte, welche es ermöglichen, sich in nicht atembarer Atmosphäre aufzuhalten",
                "c) Geräte, für Gas- und Taucheinsätze"],"correct":"b"},
    {"id":7,"level":"bronze","category":"Gerätekunde",
     "question":"Welche Schutzwirkung hat der Pressluftatmer?",
     "options":["a) Schützt den Träger vor Pressluft",
                "b) Schützt den Träger vor Atemgiften und Sauerstoffmangel",
                "c) Kann Schadstoffe aus der Umgebungsluft filtern"],"correct":"b"},
    {"id":8,"level":"bronze","category":"Gerätekunde",
     "question":"Wann muss man die Atemmasken reinigen und überprüfen?",
     "options":["a) Nach jeder Verwendung","b) Monatlich","c) 4-mal im Jahr"],"correct":"a"},
    {"id":9,"level":"bronze","category":"Gerätekunde",
     "question":"Welcher Sauerstoffgehalt ist für den Einsatz von Filtergeräten bzw. Brandfluchthauben notwendig?",
     "options":["a) Mindestens 15 Vol% Sauerstoff","b) Mindestens 17 Vol% Sauerstoff","c) Mindestens 21 Vol% Sauerstoff"],"correct":"b"},
    {"id":10,"level":"bronze","category":"Gerätekunde",
     "question":"Welche Prüfungen müssen nach einem Atemschutzeinsatz durchgeführt werden, um den Pressluftatmer wieder zu verwenden?",
     "options":["a) Sichtprüfung, Flaschenventilprüfung, Überprüfung der Warneinrichtung",
                "b) Überprüfung des Flaschendruckes und Sichtprüfung, Warnsignal Funktionstest",
                "c) Sichtprüfung (NSG, Haltegurt), Flaschendruckprüfung, Hochdruckdichtprüfung, Flaschenventilprüfung, Warnsignal Funktionstest"],"correct":"c"},
    {"id":11,"level":"bronze","category":"Gerätekunde",
     "question":"Wie viel Druckabfall ist bei der Hochdruckdichtprüfung innerhalb einer Minute maximal zulässig?",
     "options":["a) 20 bar","b) 10 bar","c) Gar keiner"],"correct":"b"},
    {"id":12,"level":"bronze","category":"Gerätekunde",
     "question":"Welchen Mindestdruck benötigen Pressluftatmer (PA) um einsatzbereit zu sein?",
     "options":["a) Mind. 200 bar beim 200 bar PA und mind. 300 bar beim 300 bar PA",
                "b) Mind. 180 bar beim 200 bar PA und mind. 270 bar beim 300 bar PA",
                "c) Mind. 150 bar beim 200 bar PA und mind. 250 bar beim 300 bar PA"],"correct":"b"},
    {"id":13,"level":"bronze","category":"Gerätekunde",
     "question":"Welcher Druck ist für den Rückmarsch des AS-Trupps erforderlich?",
     "options":["a) Mindestens 60 bar",
                "b) Rückmarschdruck = doppelter Vormarschdruckabfall, bzw. spätestens beim Ansprechen des akustischen Warnsignals",
                "c) Mindestens 50 bar"],"correct":"b"},
    {"id":14,"level":"bronze","category":"Gerätekunde",
     "question":"Welchen Zweck erfüllen Brandfluchthauben?",
     "options":["a) Sie dienen zum Retten von Personen aus sicheren Bereichen durch leicht verrauchte Bereiche mit mind. 17 Vol% Sauerstoff ins Freie bzw. sicheren Brandabschnitt",
                "b) Sie verhindern das unkontrollierte Flüchten von Personen bei Brandeinsätzen",
                "c) Sie dienen dem Einsatzleiter als Erkundungsgerät, welcher der beste Fluchtweg ist"],"correct":"a"},
    {"id":15,"level":"bronze","category":"Gerätekunde",
     "question":"Wozu dient ein Notsignalgeber?",
     "options":["a) Zur Kennzeichnung des Atemschutzgeräteträgers",
                "b) Zur Warnung des Trupps, dass eine aufgefundene Person bereits tot sein könnte",
                "c) Zur manuellen oder automatischen Abgabe eines Notsignales"],"correct":"c"},
    {"id":16,"level":"bronze","category":"Gerätekunde",
     "question":"Wozu dient ein Atemschutz-Außenüberwachungsgerät (AÜwG)?",
     "options":["a) Zur Kontrolle der Bewegung der Atemschutztrupps",
                "b) Zur Kontrolle der Einsatzzeit (Resteinsatzzeit) und Registrierung der AS-Geräteträger",
                "c) Zur Kontrolle des Rettungstrupps"],"correct":"b"},
    {"id":17,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Wann darf ein Atemschutzeinsatz begonnen werden?",
     "options":["a) Wenn es der Einsatzleiter befiehlt",
                "b) Wenn ein Rettungstrupp vor Ort ist bzw. sich auf der bestätigten Anfahrt befindet",
                "c) Wenn mind. zwei Atemschutzgeräteträger verfügbar sind"],"correct":"b"},
    {"id":18,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Wie oft muss jeder Atemschutzträger eine Atemschutzübung machen?",
     "options":["a) 2-mal im Jahr","b) 1-mal monatlich","c) 1-mal in 3 Jahren"],"correct":"a"},
    {"id":19,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Wie sichert sich ein Atemschutztrupp seinen Rückmarschweg?",
     "options":["a) Mittels Bandschlingen","b) Durch markieren mit Leuchtmittel","c) Mittels Schlauchleitung oder Leine"],"correct":"c"},
    {"id":20,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Aus wie vielen Personen besteht in der Regel ein Atemschutztrupp?",
     "options":["a) Drei","b) Vier","c) Zwei"],"correct":"c"},
    {"id":21,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Dürfen Pressluftflaschen vollkommen entleert werden?",
     "options":["a) Nein, ein Restdruck muss erhalten bleiben",
                "b) Ja, um die Luftqualität sicherzustellen",
                "c) Nein, der Druck in der Flasche muss min. 50 bar betragen"],"correct":"a"},
    {"id":22,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Wie verhält sich der Atemschutztrupp, wenn bei einem AGT die Restdruckwarneinrichtung (akustisches Warnsignal) anspricht?",
     "options":["a) Der Truppführer wird informiert und der Auftrag weiter ausgeführt",
                "b) Der gesamte Trupp tritt nach Meldung an den GK den Rückzug an",
                "c) Der Geräteträger, bei dem das Warnsignal angesprochen hat, tritt den Rückzug sofort an"],"correct":"b"},
    {"id":23,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Welche Aufgabe hat der Atemschutz-Truppführer (ASTRF) unter anderem?",
     "options":["a) Funkgerät bedienen, Strahlrohr führen, Türen öffnen, Leinen tragen, Verletzte Personen reanimieren",
                "b) Regelmäßige Druckkontrolle und rechtzeitiger Antritt des Rückzuges",
                "c) Er ist für das Funktionieren der Geräte im Trupp verantwortlich"],"correct":"b"},
    {"id":24,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Was versteht man unter Atemschutztauglichkeit?",
     "options":["a) Positiver AKL-Test, ÖFAST (jährlich absolviert) und Tagesverfassung des AGT",
                "b) Aus Pressluftatmer, Träger und Material",
                "c) Es gibt keine Voraussetzungen zur Tauglichkeit"],"correct":"a"},
    {"id":25,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Warum ist ein Pressluftatmer mit einer Restdruckwarneinrichtung ausgestattet?",
     "options":["a) Um sich akustisch bei null Sicht bemerkbar machen zu können",
                "b) Um erinnert zu werden, dass dem Gruppenkommandanten der Flaschendruck über Funk mitgeteilt werden muss",
                "c) Um auf den zu Ende gehenden Atemluftvorrat aufmerksam zu machen"],"correct":"c"},
    {"id":26,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Welche Aufgabe hat der Atemschutz-Rettungstrupp beim Atemschutzeinsatz?",
     "options":["a) Er muss für Notfälle bereitstehen und kann, wenn notwendig, unterstützende Tätigkeiten durchführen",
                "b) Er ist für die Rettung von Personen über Leitern zuständig",
                "c) Er ist für die Reserveluft zuständig"],"correct":"a"},
    {"id":27,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Wo meldet sich der aus dem Einsatz kommende Atemschutztrupp zurück?",
     "options":["a) Beim Atemschutzsammelplatz",
                "b) Bei dem für den Atemschutzeinsatz zuständigen Gruppenkommandanten mit der Außenüberwachung",
                "c) Bei der Einsatzleitung"],"correct":"b"},
    {"id":28,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Was ist zu tun, wenn durch die Atemmaske oder den Lungenautomaten Rauch eindringt?",
     "options":["a) Luft anhalten und Einsatzstelle sofort verlassen",
                "b) Wenn vorhanden, mittels Zuschuss(Dusch)knopf am Lungenautomaten Atemluft zuschießen und Einsatzstelle sofort gemeinsam (ganzer AS-Trupp) verlassen",
                "c) Lungenautomat abschrauben und wechseln"],"correct":"b"},
    {"id":29,"level":"bronze","category":"Allgemeine Fragen",
     "question":"In welchen Abständen ist der ÖFAST in der Feuerwehr durchzuführen?",
     "options":["a) Jährlich (+ 5 Monate)","b) Einmal im Jahr (+/- 4 Monate)","c) Jährlich (+/- 3 Monate)"],"correct":"c"},
    {"id":30,"level":"bronze","category":"Allgemeine Fragen",
     "question":"Wie ist die allgemeine Vorgehensweise in Räumen mit wenig bzw. NULL Sicht?",
     "options":["a) Seitenkriechgang, der Wand entlang, Rauchabzug herstellen, Rückzug sichern, zusammenbleiben",
                "b) Einzeln eintreten, Rauchabzug herstellen",
                "c) Im Trupp zusammenbleiben und der Wand entlang aufrecht gehen, Rauchabzug herstellen"],"correct":"a"},
]

# ── SILVER – Stufe 2 ──────────────────────────────────────────────────────────
QUESTIONS_SILVER = [
    {"id":31,"level":"silver","category":"Atmung",
     "question":"Was ist Kohlenstoffmonoxid für ein Atemgift?",
     "options":["a) Erstickend wirkendes Gift","b) Blut und Nervengift","c) Reiz- und Ätzgift"],"correct":"b"},
    {"id":32,"level":"silver","category":"Atmung",
     "question":"Wie kann man Sauerstoffmangel in der Umgebungsluft erkennen?",
     "options":["a) Nur mit speziellen Messgeräten","b) An der blauen Färbung der Luft","c) Durch Kerzen Schnelltests"],"correct":"a"},
    {"id":33,"level":"silver","category":"Atmung",
     "question":"Woran erkennt man eine gesunde Atemtechnik?",
     "options":["a) Am ruhigen Ein- und Ausatmen","b) An der langsamen Brustatmung","c) An der beständigen, pausenlosen Atmung unter Beachtung der Atemgymnastik"],"correct":"a"},
    {"id":34,"level":"silver","category":"Atmung",
     "question":"Welche Folge kann eine gestörte Atmung (Atemkrise) hervorrufen?",
     "options":["a) Rauschzustände","b) Lebensgefahr","c) Depressionen"],"correct":"b"},
    {"id":35,"level":"silver","category":"Atmung",
     "question":"Was geschieht mit der Atemluft in der Lunge?",
     "options":["a) Teile des Stickstoffes werden vom Blut aufgenommen, Kohlendioxid abtransportiert",
                "b) Sauerstoff wird vom Blut aufgenommen, Kohlenstoffdioxid vom Blut in die Lunge (Gasaustausch) abgegeben",
                "c) Kohlendioxid (CO2) wird an das Blut übertragen, um das Atemzentrum anzuregen"],"correct":"b"},
    {"id":36,"level":"silver","category":"Atmung",
     "question":"In welcher Form können atemschädliche Stoffe in der Luft vorkommen?",
     "options":["a) Nur gasförmig","b) Als Partikel, Gase und Dämpfe","c) Nur in Kombination mit Aerosolen"],"correct":"b"},
    {"id":37,"level":"silver","category":"Atmung",
     "question":"Wann muss ein Atemschutzgeräteträger zur ärztlichen Nachuntersuchung (AKL-Test)?",
     "options":["a) Jährlich",
                "b) Bis zum 40. Lebensjahr alle 5 Jahre, zwischen 40. und 50. Lebensjahr alle 3 Jahre, ab dem 50. Lebensjahr alle 2 Jahre oder nach schwerer Erkrankung",
                "c) Alle 3 Jahre bis zum 40. Lebensjahr, alle 2 Jahre bis zum 60. Lebensjahr, danach jährlich"],"correct":"b"},
    {"id":38,"level":"silver","category":"Atmung",
     "question":"Wie kann man einer Atemkrise entgegenwirken?",
     "options":["a) Durch schnelle Atemzüge","b) Durch ruhiges, tiefes Ein- und Ausatmen","c) Durch Drücken des Zuschussknopfes am Lungenautomaten"],"correct":"b"},
    {"id":39,"level":"silver","category":"Atmung",
     "question":"Wie viel Luft veratmet ein AGT durchschnittlich bei einem Atemschutzeinsatz?",
     "options":["a) 20 – 30 Liter/min","b) 60 – 90 Liter/min","c) 40 – 50 Liter/min"],"correct":"c"},
    {"id":40,"level":"silver","category":"Gerätekunde",
     "question":"Was hat auf jedem Pressluftatmer (PA) zumindest montiert zu sein?",
     "options":["a) Ein Notsignalgeber","b) Keile und Bandschlingen","c) Ein Haltegurt mit zusätzlichen Karabinern"],"correct":"a"},
    {"id":41,"level":"silver","category":"Gerätekunde",
     "question":"Warum werden bei der Feuerwehr Kombinationsfilter verwendet?",
     "options":["a) Weil er in Kombination mit der Atemschutzmaske Schutz vor mehreren Gasen bietet",
                "b) Damit ein Schutz vor Gasen und Partikeln gegeben ist",
                "c) Kombinationsfilter sind mit allen Masken kompatibel"],"correct":"b"},
    {"id":42,"level":"silver","category":"Gerätekunde",
     "question":"Schützen Filtergeräte gegen Sauerstoffmangel?",
     "options":["a) Ja","b) Bedingt","c) Nein"],"correct":"c"},
    {"id":43,"level":"silver","category":"Gerätekunde",
     "question":"Wogegen schützt die Brandfluchthaube?",
     "options":["a) Gegen Brandrauch ausschließlich Kohlenstoffmonoxid",
                "b) Nur gegen Kohlenstoffmonoxid",
                "c) Kurzzeitig gegen verschiedene Atemgifte einschließlich Kohlenstoffmonoxid"],"correct":"c"},
    {"id":44,"level":"silver","category":"Gerätekunde",
     "question":"Welcher Bauteil der Atemmaske sorgt für die Sprechverbindung nach außen?",
     "options":["a) Die Sprechmembrane","b) Das Mikrofon bei Funkmasken","c) Der Hohlraum in der Innenmaske"],"correct":"a"},
    {"id":45,"level":"silver","category":"Gerätekunde",
     "question":"Welches Ventil ist für die Dichtheit der Maske besonders wichtig?",
     "options":["a) Das Einatemventil","b) Das Ausatemventil","c) Das Steuerventil"],"correct":"b"},
    {"id":46,"level":"silver","category":"Gerätekunde",
     "question":"Wer führt die Pflege der Atemmasken nach der Verwendung durch?",
     "options":["a) Der Atemschutzwart mit Unterstützung der Geräteträger",
                "b) Der Geräteträger",
                "c) Der Gerätemeister, der Atemschutzwart überwacht und prüft"],"correct":"a"},
    {"id":47,"level":"silver","category":"Gerätekunde",
     "question":"Warum sind Atemmasken mit einer Innenmaske ausgestattet?",
     "options":["a) Zur Erleichterung der Wartung",
                "b) Um eine angenehme Luftführung zu erreichen",
                "c) Verkleinerung des Totraumes, das Beschlagen der Sichtscheibe wird weitgehend verhindert"],"correct":"c"},
    {"id":48,"level":"silver","category":"Gerätekunde",
     "question":"Wie viele AS-Trupps können mit einem Außenüberwachungsgerät (Modell Steiermark) zeitgleich überwacht werden?",
     "options":["a) Zwei","b) Drei","c) Vier"],"correct":"b"},
    {"id":49,"level":"silver","category":"Gerätekunde",
     "question":"Welche Funktion hat der Lungenautomat?",
     "options":["a) Abgabe der Atemluft an den Atemschutzgeräteträger entsprechend seines Bedarfs",
                "b) Er verringert den Widerstand beim Atmen",
                "c) Er reduziert den Luftdruck von Hochdruck auf Niederdruck"],"correct":"a"},
    {"id":50,"level":"silver","category":"Gerätekunde",
     "question":"Darf mit einem Pressluftatmer getaucht werden?",
     "options":["a) Nur bis fünf Meter","b) Nein","c) Ja, aber nur mit Tauchmaske"],"correct":"b"},
    {"id":51,"level":"silver","category":"Gerätekunde",
     "question":"Wer darf defekte Atemschutzgeräte und Atemmasken reparieren?",
     "options":["a) Die Hersteller und autorisierte Atemschutzwerkstätten (z.B.: LFV Steiermark)",
                "b) Der Atemschutzwart der Feuerwehr",
                "c) Jeder mit Atemschutzgeräteträger Lehrgang"],"correct":"a"},
    {"id":52,"level":"silver","category":"Gerätekunde",
     "question":"Welches Volumen / Druck können Pressluftflaschen für Atemschutzgeräte haben?",
     "options":["a) 4 Liter / 200 bar; 6 Liter / 300 bar; 6,8 Liter / 300 bar",
                "b) 2 Liter / 300 bar; 4 Liter / 300 bar; 15 Liter / 200 bar",
                "c) 6,8 Liter / 200 bar; 6 Liter / 200 bar; 4 Liter / 300 bar"],"correct":"a"},
    {"id":53,"level":"silver","category":"Allgemeine Fragen",
     "question":"Kann ein (Voll)Bartträger als Atemschutzgeräteträger eingesetzt werden?",
     "options":["a) Ja, mit Überdruckmaske",
                "b) Es ist egal ob man einen Vollbart hat",
                "c) Nein, der dichte Sitz der Atemmaske ist nicht mehr gewährleistet"],"correct":"c"},
    {"id":54,"level":"silver","category":"Allgemeine Fragen",
     "question":"Im Trupp löst ein Notsignalgeber aus. Was ist sofort zu tun?",
     "options":["a) Einsatzauftrag abschließen, danach sich um das Signal kümmern",
                "b) Einsatzauftrag abbrechen, Kontakt mit dem Truppmitglied aufnehmen, Hilfe leisten",
                "c) Trupp teilen, ein Mitglied kümmert sich um das Notsignal, das andere setzt den Einsatzauftrag fort"],"correct":"b"},
    {"id":55,"level":"silver","category":"Allgemeine Fragen",
     "question":"Wann muss der GK als Außenüberwacher mit dem Atemschutztrupp Funkkontakt aufnehmen?",
     "options":["a) Alle 5 Minuten um den Flaschendruck zu kontrollieren",
                "b) Bei Einsatzbeginn (Funkprobe); gegebenenfalls bei 20, immer bei 10, und 0 Minuten Resteinsatzzeit",
                "c) Bei Einsatzbeginn und bei Einsatzende"],"correct":"b"},
    {"id":56,"level":"silver","category":"Allgemeine Fragen",
     "question":"Wer trägt für die Außenüberwachung des AS-Trupps die Verantwortung?",
     "options":["a) Der Gruppenkommandant",
                "b) Der Leiter des Atemschutzsammelplatzes",
                "c) Der Atemschutzbeauftragte der Feuerwehr"],"correct":"a"},
    {"id":57,"level":"silver","category":"Allgemeine Fragen",
     "question":"Mindestalter für Atemschutzgeräteträger?",
     "options":["a) 20 Jahre ohne Grundausbildung","b) 16 Jahre mit Grundausbildung","c) Vollendetes 18. Lebensjahr"],"correct":"c"},
    {"id":58,"level":"silver","category":"Allgemeine Fragen",
     "question":"Was ist vor Beendigung des Atemschutzeinsatzes (z.B. Brandeinsatz) zu beachten?",
     "options":["a) Alarmierung des Atemschutzbereichsbeauftragten",
                "b) Organisation von Speisen, Getränken und Rauchwaren",
                "c) Eine Grobdekontamination ist noch am Einsatzort durchzuführen"],"correct":"c"},
    {"id":59,"level":"silver","category":"Allgemeine Fragen",
     "question":"Warum soll jedes mit Atemschutz ausgestattete Feuerwehrfahrzeug mit einem Außenüberwachungsgerät ausgestattet sein?",
     "options":["a) Damit jeder Atemschutztrupp von Beginn des Einsatzes an überwacht werden kann",
                "b) Damit ausreichend Reservegeräte vorhanden sind",
                "c) Damit eine Funkverbindung zu den eingesetzten Atemschutztrupps aufgebaut werden kann"],"correct":"a"},
    {"id":60,"level":"silver","category":"Allgemeine Fragen",
     "question":"Wann hat ein in Bereitschaft stehender AS-Rettungstrupp die Atemmaske nicht aufgesetzt?",
     "options":["a) Wenn sich nur ein Angriffstrupp im Gefahrenbereich befindet",
                "b) Wenn durch die Witterung oder die Technik der Atemmaske die Sichtscheibe innen beschlägt",
                "c) Wenn eine Lagerung in der Maskendose möglich ist"],"correct":"b"},
]


# ── GOLD – Stufe 3 ────────────────────────────────────────────────────────────
QUESTIONS_GOLD = [
    {"id":61,"level":"gold","category":"Gerätekunde",
     "question":"Was steht im oberen Teil der orangen Warntafel (Gefahrguttransport)?",
     "options":["a) Gefahrnummer","b) Stoffnummer","c) Gefährliche Güternummer"],"correct":"a"},
    {"id":62,"level":"gold","category":"Gerätekunde",
     "question":"Was bedeutet ein \"X\" vor der Gefahrenummer?",
     "options":["a) Es bezeichnet, dass der Stoff in gefährlicher Weise mit Wasser reagiert",
                "b) Der Stoff kann mit Wasser in Berührung kommen",
                "c) Der Stoff darf nicht mit Luft in Berührung kommen"],"correct":"a"},
    {"id":63,"level":"gold","category":"Gerätekunde",
     "question":"Wann müssen Pressluftflaschen aus Stahl von einem autorisierten Sachverständigen grundsätzlich überprüft werden?",
     "options":["a) Alle 5 Jahre","b) Alle 6 Jahre","c) Alle 10 Jahre"],"correct":"c"},
    {"id":64,"level":"gold","category":"Gerätekunde",
     "question":"Zu welcher Schutzstufe gehört der gasdichte Chemikalienschutzanzug?",
     "options":["a) Schutzstufe 1","b) Schutzstufe 3","c) Schutzstufe 2"],"correct":"a"},
    {"id":65,"level":"gold","category":"Gerätekunde",
     "question":"Wie groß ist die Mindestabsperrgrenze bei Gefahrguteinsätzen?",
     "options":["a) Mindestens 10 Meter","b) 30 – 60 Meter","c) Maximal 30 Meter"],"correct":"b"},
    {"id":66,"level":"gold","category":"Gerätekunde",
     "question":"Welche Atemluftversorgung benötigt man bei gasdichten Chemikalienschutzanzügen?",
     "options":["a) Pressluftatmer mit akustischer Restdruckwarnung, zusätzlich sind Druckluftschlauchgeräte möglich",
                "b) Pressluftatmer mit manueller Restdruckwarnung und doppelten Pressluftflaschen",
                "c) Fremdversorgung mit Restdruckwarnung"],"correct":"a"},
    {"id":67,"level":"gold","category":"Gerätekunde",
     "question":"Wann ist ein Schutzanzug der Schutzstufe 3 zu überprüfen?",
     "options":["a) Nach jeder Verwendung, ansonsten jährlich",
                "b) Nur nach Einsätzen, zusätzlich alle 2 Jahre",
                "c) Halbjährlich"],"correct":"a"},
    {"id":68,"level":"gold","category":"Gerätekunde",
     "question":"In welchen Zeitabständen müssen Pressluftatmer einer Grundüberholung unterzogen werden?",
     "options":["a) Jährlich",
                "b) Alle 6; 9 bzw. 10 Jahre, je nach Hersteller und Type",
                "c) Nach persönlichem Dafürhalten des Atemschutzwartes"],"correct":"b"},
    {"id":69,"level":"gold","category":"Gerätekunde",
     "question":"Auf welchen Mitteldruck (bar) reduziert der Druckminderer durchschnittlich den Hochdruck beim Pressluftatmer?",
     "options":["a) 5 bis 9 bar","b) 4 bis 8 bar","c) 6 bis 9 bar"],"correct":"c"},
    {"id":70,"level":"gold","category":"Allgemeine Fragen",
     "question":"Wem kann der Gruppenkommandant die Bedienung des Außenüberwachungsgerätes (AÜwG) delegieren?",
     "options":["a) Seinem Melder oder Maschinisten",
                "b) Dem Melder des Einsatzleiters",
                "c) Dem Strahlrohrführer"],"correct":"a"},
    {"id":71,"level":"gold","category":"Allgemeine Fragen",
     "question":"Ein ASTRF hört nach 25 Minuten das akustische Warnsignal des ASTRM2. Manometer: ASTRF 70 bar, ASTRM1 110 bar, ASTRM2 85 bar. Was ist zu tun?",
     "options":["a) Der Trupp zieht sich zurück, weil der ASTRF einen Manometerdefekt beim PA des ASTRM2 vermutet",
                "b) Der Trupp verbleibt im Einsatz, weil die Manometerkontrolle ausreichenden Luftvorrat zeigt",
                "c) Der Trupp setzt den Einsatz fort, bis bei allen Geräten das akustische Warnsignal anspricht"],"correct":"a"},
    {"id":72,"level":"gold","category":"Allgemeine Fragen",
     "question":"Wer ordnet den Beginn des Druckbelüftungsvorganges an?",
     "options":["a) Der Atemschutztruppführer (ASTRF)","b) Der Einsatzleiter","c) Der Gruppenkommandant"],"correct":"c"},
    {"id":73,"level":"gold","category":"Allgemeine Fragen",
     "question":"Wofür steht die \"GAMS\" Regel der Feuerwehr?",
     "options":["a) Gefahr erkennen, Absichern, Menschenrettung, Schutzausrüstung anlegen",
                "b) Gefahr erkennen, Absperren, Messen, Spezialkräfte anfordern",
                "c) Gefahr erkennen, Absperren, Menschenrettung, Spezialkräfte anfordern"],"correct":"b"},
    {"id":74,"level":"gold","category":"Allgemeine Fragen",
     "question":"Was bedeutet die \"3A Regel\"?",
     "options":["a) Abschirmung groß halten, Abstand verkürzen, Aufenthaltszeit verlängern",
                "b) Möglichst gute Abschirmung, großen Abstand und kurze Aufenthaltszeit",
                "c) Abschirmung entfernen, Abstand verkürzen, Aufenthaltszeit kurz halten"],"correct":"b"},
    {"id":75,"level":"gold","category":"Allgemeine Fragen",
     "question":"Ein Angriffstrupp will in einen Raum mit dichtem und heißem Brandrauch vorgehen. Was ist zu tun?",
     "options":["a) Den heißen Brandrauch sofort mit Sprühstrahl bis zur Rauchuntergrenze kühlen",
                "b) Mit Vollstrahl den Brandherd zu treffen versuchen",
                "c) Einige Minuten warten, wie sich die Lage entwickelt"],"correct":"a"},
    {"id":76,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Umstände schließen einen Innenangriff aus?",
     "options":["a) Das Gebäude ist nicht stromlos geschaltet",
                "b) Wenn die mögliche Gefährdung des AS-Trupps nicht dafür spricht (Einsturz-, Explosionsgefahr usw.)",
                "c) Im Gebäude befinden sich keine Menschen mehr"],"correct":"b"},
    {"id":77,"level":"gold","category":"Allgemeine Fragen",
     "question":"Wer gibt den Befehl für den Einsatz des Atemschutztrupps in der Löschgruppe?",
     "options":["a) Der Gruppenkommandant","b) Der Einsatzleiter","c) Der Leiter des Atemschutzsammelplatzes"],"correct":"a"},
    {"id":78,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Farbkennzeichnung am Flaschenhals haben Acetylengasflaschen in Österreich?",
     "options":["a) Weiß","b) Rot","c) Kastanienbraun"],"correct":"c"},
    {"id":79,"level":"gold","category":"Allgemeine Fragen",
     "question":"Mit welcher Farbe sind am Flaschenhals Druckgasflaschen für brennbare Gase, außer Acetylen, gekennzeichnet?",
     "options":["a) Weiß","b) Rot","c) Kastanienbraun"],"correct":"b"},
    {"id":80,"level":"gold","category":"Allgemeine Fragen",
     "question":"Wieviel von seiner Tragfähigkeit verliert ein Stahlträger bei einer Temperatur von 700 Grad Celsius?",
     "options":["a) Nichts","b) 25 %","c) Zwei Drittel"],"correct":"c"},
    {"id":81,"level":"gold","category":"Allgemeine Fragen",
     "question":"Womit kann eine explosionsfähige Atmosphäre am Einsatzort nachgewiesen werden?",
     "options":["a) Mit einem Explosimeter","b) Mit einem Kompressor","c) Mit einer Waage"],"correct":"a"},
    {"id":82,"level":"gold","category":"Allgemeine Fragen",
     "question":"Worüber gibt die Stoffnummer (UN-Nummer) Auskunft?",
     "options":["a) Name des Fahrzeuges","b) Über die Menge","c) Kennzeichnung des Stoffes"],"correct":"c"},
    {"id":83,"level":"gold","category":"Allgemeine Fragen",
     "question":"Was ist beim Einsatz eines AS-Trupps auf dem Außenüberwachungsgerät zu notieren bzw. zu beachten?",
     "options":["a) Einsatzleiter, Gruppenkommandant, Zeiten, Flaschendrücke, Rettungstrupp, Einsatzadresse",
                "b) Verantwortlicher, Einsatzabschnitt, Namen der Truppmitglieder, Geräteart, Einsatzbeginn/-ende, Soll-Rückzugsdruck, niedrigste Flaschendrücke, Befehl, Lagemeldungen, Rettungstrupp und dessen niedrigsten Flaschendruck",
                "c) Sammelplatzleiter, Einsatzleiter, Namen der Truppmitglieder, Lagemeldungen, Rettungstrupp, Zeiten, Flaschendrücke"],"correct":"b"},
    {"id":84,"level":"gold","category":"Allgemeine Fragen",
     "question":"Was ist beim Erkennen von \"Gefahr in Verzug\" zu tun?",
     "options":["a) Sofortiger Rückzug der Trupps, Meldung beim Gruppenkommandanten",
                "b) Gruppenkommandanten fragen, ob Rückzug durchgeführt werden soll",
                "c) Einsatzleiter Bescheid geben"],"correct":"a"},
    {"id":85,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welcher Sicherheitsabstand ist bei der Brandbekämpfung im Bereich elektrischer Anlagen bis 1000 V beim Einsatz von C-Mehrzweckstrahlrohren mit reinem Wasser einzuhalten?",
     "options":["a) Sprühstrahl 1 m – Vollstrahl 5 m",
                "b) Sprühstrahl 5 m – Vollstrahl 1 m",
                "c) Sprühstrahl 5 m – Vollstrahl 10 m"],"correct":"a"},
    {"id":86,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welches Löschmittel darf bei Fettbränden nicht eingesetzt werden?",
     "options":["a) Fettbrandlöscher","b) Wasser","c) Löschpulver"],"correct":"b"},
    {"id":87,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Strahlrohreinstellung wird vorzugsweise bei Innenangriffen eingesetzt?",
     "options":["a) Vollstrahl","b) Spülen","c) Sprühstrahl"],"correct":"c"},
    {"id":88,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Druckzonen bilden sich bei einer Verbrennung?",
     "options":["a) Gefährliche und ungefährliche Zone",
                "b) Neutrale Zone, Überdruckzone, Unterdruckzone",
                "c) Grüne, gelbe und rote Zone"],"correct":"b"},
    {"id":89,"level":"gold","category":"Allgemeine Fragen",
     "question":"Wann ist die komplette Einsatzbekleidung \"E1\" zu tragen?",
     "options":["a) Bei jedem Einsatz und jeder Übung mit Brandgefahr",
                "b) Bei jedem Einsatz",
                "c) Nur beim Atemschutzeinsatz"],"correct":"a"},
    {"id":90,"level":"gold","category":"Allgemeine Fragen",
     "question":"Wie kann man Säuredämpfe niederschlagen?",
     "options":["a) Mit Feuerpatschen","b) Mit Wassersprühstrahl","c) Mit Laugenpulver"],"correct":"b"},
    {"id":91,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Stoffe neigen zu Selbstentzündung?",
     "options":["a) Phosphor, in Öl getränkte Putzwolle, feuchtes Heu",
                "b) Benzin, Benzol, Kerosin, Teer, Bitumen",
                "c) Seifen, Putzmittel, Bleichmittel"],"correct":"a"},
    {"id":92,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Prüfungen hat der Atemschutzwart monatlich durchzuführen?",
     "options":["a) Sichtkontrolle, ob die Beladung in Ordnung ist",
                "b) Kontrolle der Atemschutzgeräte (PA, Notsignalgeber, Atemmaske und Filter), Druck der Reserveflaschen, Außenüberwachungsgerät, Wärmebildkamera",
                "c) Sicht-, Dicht- und Funktionsprüfung"],"correct":"b"},
    {"id":93,"level":"gold","category":"Allgemeine Fragen",
     "question":"Bei welchem Brand ist die Kohlenstoffmonoxidbildung besonders groß?",
     "options":["a) Bränden in geschlossenen Räumen","b) Bei Metallbränden","c) Bei Waldbränden"],"correct":"a"},
    {"id":94,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Bekleidung ist für die Menschenrettung bei Einsätzen mit gefährlichen Stoffen im Freien zumindest zu tragen?",
     "options":["a) Chemikalienschutzanzug Stufe 2",
                "b) Einsatzoverall mit Filtergerät",
                "c) Schutzbekleidung für die Brandbekämpfung, Einmalhandschuhe, darüber Chemikalienschutzhandschuhe und chemikalienbeständige Sicherheitsstiefel, Feuerschutzhaube"],"correct":"c"},
    {"id":95,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Bekleidung ist bei Einsätzen am Brandgeschehen zu tragen?",
     "options":["a) Hitzeschutzanzug nach EN 1486",
                "b) Einsatzoverall",
                "c) Schutzbekleidung für die Brandbekämpfung nach EN 469"],"correct":"c"},
    {"id":96,"level":"gold","category":"Allgemeine Fragen",
     "question":"Was versteht man unter einem Einsatzabschnitt?",
     "options":["a) Zeitliche Einteilung in Erkundungsphase, Verteidigungs- und Angriffsphase",
                "b) Teil einer Einsatzstelle, der von der Einsatzleitung einer Einheit zugewiesen wird",
                "c) Bereiche an einer Einsatzstelle, in der Feuerwehren eines BFV arbeiten"],"correct":"b"},
    {"id":97,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche giftigen Stoffe und Gefahren gehen von brennenden PVC aus?",
     "options":["a) Salzsäuredämpfe, Bildung heißer Tropfen",
                "b) Sichtbehinderung durch weißen Rauch und grelle Flammen",
                "c) Unsichtbare Flammen"],"correct":"a"},
    {"id":98,"level":"gold","category":"Allgemeine Fragen",
     "question":"Von wie vielen Personen darf eine 2-teilige Schiebeleiter gleichzeitig bestiegen werden?",
     "options":["a) Max. 1 Person",
                "b) Von 1 Person, ausgenommen bei Menschenrettung von 2 Personen (= Retter und zu rettende Person)",
                "c) Max. 3 Personen"],"correct":"b"},
    {"id":99,"level":"gold","category":"Allgemeine Fragen",
     "question":"Gegen welches gefährliche Atemgift schützt ein Filter vom Typ \"ABEK2-P3\" nicht?",
     "options":["a) Kohlenstoffmonoxid","b) Blausäuredämpfe","c) Chlorgas"],"correct":"a"},
    {"id":100,"level":"gold","category":"Allgemeine Fragen",
     "question":"Welche Maßnahmen sind bei Druckgefäßen im Brandgeschehen zu treffen?",
     "options":["a) Druckgefäße bergen und im Freien in ein Kühlbecken ablegen",
                "b) Kennzeichnung ablesen, um Inhalt zu identifizieren",
                "c) Aus sicherer Deckung heraus kühlen"],"correct":"c"},
]

ALL_QUESTIONS = {"bronze": QUESTIONS_BRONZE, "silver": QUESTIONS_SILVER, "gold": QUESTIONS_GOLD}


# ── SESSION HELPERS ───────────────────────────────────────────────────────────
# KEY FIX: never store full question dicts in the session cookie (4 KB limit).
# Store only a small list of integer indices + level string.

def build_indices(lv, mode):
    """Return a (possibly shuffled/filtered) list of indices into ALL_QUESTIONS[lv].
    For lv='all', indices are encoded as (level_key, index) pairs flattened into
    a special combined list stored separately in the session."""
    if lv == "all":
        # Return flat list — handled specially; we reuse q_indices as flat combined list
        combined = []
        for sub_lv in ("bronze", "silver", "gold"):
            for i in range(len(ALL_QUESTIONS[sub_lv])):
                combined.append((sub_lv, i))
        random.shuffle(combined)
        return combined  # list of (lv, idx) tuples
    source = ALL_QUESTIONS[lv]
    if mode == "atmung":
        idxs = [i for i, q in enumerate(source) if q["category"] == "Atmung"]
    elif mode == "allgemein":
        idxs = [i for i, q in enumerate(source) if q["category"] == "Allgemeine Fragen"]
    else:
        idxs = list(range(len(source)))
    if mode == "shuffle":
        random.shuffle(idxs)
    return idxs


def session_questions():
    """Reconstruct the active question list from stored indices — always small."""
    lv = session.get("level", "bronze")
    idxs = session.get("q_indices", [])
    if lv == "all":
        result = []
        for entry in idxs:
            sub_lv, i = entry[0], entry[1]
            src = ALL_QUESTIONS.get(sub_lv, [])
            if i < len(src):
                result.append(src[i])
        return result
    src = ALL_QUESTIONS.get(lv, [])
    return [src[i] for i in idxs if i < len(src)]


# ── JINJA2 RENDER ─────────────────────────────────────────────────────────────
def j2(tmpl, **ctx):
    from jinja2 import Environment
    return Environment().from_string(tmpl).render(**ctx)


BASE = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Atemschutz Training</title>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',system-ui,sans-serif;background:#0f1117;color:#e2e8f0;
         min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:2rem 1rem}
    .container{width:100%;max-width:720px}
    header{text-align:center;margin-bottom:2rem}
    header h1{font-size:1.4rem;font-weight:700;color:#f97316;letter-spacing:.02em}
    header p{font-size:.85rem;color:#64748b;margin-top:.3rem}
    .level-pill{display:inline-flex;align-items:center;gap:.4rem;font-size:.75rem;font-weight:700;
      letter-spacing:.06em;text-transform:uppercase;border-radius:99px;padding:.2rem .8rem;
      margin-top:.5rem;border:1px solid}
    .level-pill.bronze{color:#cd7f32;border-color:rgba(205,127,50,.4);background:rgba(205,127,50,.1)}
    .level-pill.silver{color:#b0c0d4;border-color:rgba(148,163,184,.4);background:rgba(148,163,184,.1)}
    .level-pill.gold{color:#eab308;border-color:rgba(234,179,8,.4);background:rgba(234,179,8,.1)}
    .level-pill.all{color:#a78bfa;border-color:rgba(167,139,250,.4);background:rgba(167,139,250,.1)}
    .progress-wrap{background:#1e2433;border-radius:99px;height:6px;margin-bottom:1.5rem;overflow:hidden}
    .progress-bar{height:100%;border-radius:99px;transition:width .4s ease}
    .progress-bar.bronze{background:linear-gradient(90deg,#cd7f32,#e8a460)}
    .progress-bar.silver{background:linear-gradient(90deg,#64748b,#94a3b8)}
    .progress-bar.gold{background:linear-gradient(90deg,#ca8a04,#eab308)}
    .progress-bar.all{background:linear-gradient(90deg,#7c3aed,#a78bfa)}
    .progress-label{display:flex;justify-content:space-between;font-size:.78rem;color:#475569;margin-bottom:.5rem}
    .card{background:#1a2035;border:1px solid #2d3748;border-radius:14px;padding:1.8rem 2rem;margin-bottom:1.2rem}
    .category-badge{display:inline-block;font-size:.72rem;font-weight:600;letter-spacing:.08em;
      text-transform:uppercase;border-radius:99px;padding:.2rem .75rem;margin-bottom:1rem}
    .category-badge.bronze{color:#cd7f32;background:rgba(205,127,50,.1);border:1px solid rgba(205,127,50,.25)}
    .category-badge.silver{color:#94a3b8;background:rgba(148,163,184,.1);border:1px solid rgba(148,163,184,.25)}
    .category-badge.gold{color:#eab308;background:rgba(234,179,8,.1);border:1px solid rgba(234,179,8,.25)}
    .category-badge.all{color:#a78bfa;background:rgba(167,139,250,.1);border:1px solid rgba(167,139,250,.25)}
    .question-num{font-size:.8rem;color:#475569;margin-bottom:.4rem}
    .question-text{font-size:1.05rem;font-weight:600;line-height:1.5;color:#f1f5f9;margin-bottom:1.4rem}
    .options{display:flex;flex-direction:column;gap:.65rem}
    .option{display:flex;align-items:flex-start;gap:.75rem;background:#0f1117;border:1px solid #2d3748;
      border-radius:10px;padding:.85rem 1rem;cursor:pointer;transition:border-color .15s,background .15s;
      text-align:left;font-size:.92rem;color:#cbd5e1;line-height:1.45;width:100%}
    .option.hb:hover:not(:disabled){border-color:#cd7f32;background:rgba(205,127,50,.07);color:#f1f5f9}
    .option.hs:hover:not(:disabled){border-color:#94a3b8;background:rgba(148,163,184,.07);color:#f1f5f9}
    .option.hg:hover:not(:disabled){border-color:#eab308;background:rgba(234,179,8,.07);color:#f1f5f9}
    .option.ha:hover:not(:disabled){border-color:#a78bfa;background:rgba(167,139,250,.07);color:#f1f5f9}
    .option .key{font-weight:700;color:#94a3b8;min-width:1.2rem;flex-shrink:0}
    .option.correct{border-color:#22c55e!important;background:rgba(34,197,94,.08)!important;color:#86efac!important}
    .option.correct .key{color:#22c55e}
    .option.wrong{border-color:#ef4444!important;background:rgba(239,68,68,.08)!important;color:#fca5a5!important}
    .option.wrong .key{color:#ef4444}
    .option:disabled{cursor:default}
    .feedback{margin-top:1rem;font-size:.88rem;padding:.65rem 1rem;border-radius:8px;display:none}
    .feedback.show{display:block}
    .feedback.ok{background:rgba(34,197,94,.1);color:#86efac;border:1px solid rgba(34,197,94,.25)}
    .feedback.err{background:rgba(239,68,68,.1);color:#fca5a5;border:1px solid rgba(239,68,68,.25)}
    .btn{display:inline-block;padding:.7rem 1.6rem;border-radius:10px;border:none;font-size:.95rem;
      font-weight:600;cursor:pointer;transition:opacity .15s,transform .1s;text-decoration:none}
    .btn:active{transform:scale(.97)}
    .btn-bronze{background:#cd7f32;color:#fff}.btn-bronze:hover{opacity:.88}
    .btn-silver{background:#4b5e73;color:#e2e8f0}.btn-silver:hover{opacity:.88}
    .btn-gold{background:#a16207;color:#fef9c3}.btn-gold:hover{opacity:.88}
    .btn-all{background:#5b21b6;color:#ede9fe}.btn-all:hover{opacity:.88}
    .btn-ghost{background:#1e2433;color:#94a3b8;border:1px solid #2d3748}
    .btn-ghost:hover{border-color:#475569;color:#cbd5e1}
    .nav-row{display:flex;justify-content:space-between;align-items:center;margin-top:1.2rem;gap:1rem}
    .result-card{text-align:center;padding:2.5rem}
    .result-score{font-size:4rem;font-weight:800;line-height:1;margin-bottom:.5rem}
    .result-score.bronze{color:#cd7f32}.result-score.silver{color:#94a3b8}.result-score.gold{color:#eab308}.result-score.all{color:#a78bfa}
    .result-sub{font-size:1rem;color:#64748b;margin-bottom:1.5rem}
    .result-verdict{font-size:1.1rem;font-weight:600;padding:.6rem 1.4rem;border-radius:99px;display:inline-block;margin-bottom:2rem}
    .verdict-pass{background:rgba(34,197,94,.12);color:#22c55e;border:1px solid rgba(34,197,94,.3)}
    .verdict-fail{background:rgba(239,68,68,.12);color:#ef4444;border:1px solid rgba(239,68,68,.3)}
    .category-stats{display:flex;flex-direction:column;gap:.5rem;margin-bottom:2rem;text-align:left}
    .cat-row{display:flex;align-items:center;justify-content:space-between;background:#0f1117;
      border:1px solid #2d3748;border-radius:8px;padding:.6rem 1rem;font-size:.88rem}
    .cat-row .cat-name{color:#94a3b8}.cat-row .cat-score{font-weight:700;color:#f1f5f9}
    .start-card{text-align:center;padding:2.5rem}
    .start-card h2{font-size:1.3rem;font-weight:700;color:#f1f5f9;margin-bottom:.5rem}
    .start-card p{color:#64748b;font-size:.9rem;margin-bottom:1.8rem;line-height:1.6}
    .level-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.8rem}
    .level-card{border-radius:14px;border:2px solid #2d3748;padding:1.5rem 1rem;cursor:pointer;
      transition:border-color .15s,background .15s;text-decoration:none;
      display:flex;flex-direction:column;align-items:center;gap:.5rem}
    .level-card:hover{background:#1e2433}
    .level-card.bc:hover{border-color:#cd7f32}
    .level-card.sc:hover{border-color:#94a3b8}
    .level-card.gc:hover{border-color:#eab308}
    .level-card.rc:hover{border-color:#a78bfa}
    .level-icon{font-size:2.5rem}
    .level-title{font-size:1.1rem;font-weight:700}
    .bc .level-title{color:#cd7f32}.sc .level-title{color:#94a3b8}.gc .level-title{color:#eab308}.rc .level-title{color:#a78bfa}
    .level-sub{font-size:.78rem;color:#475569}
    .mode-grid{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-bottom:1.5rem}
    .mode-btn{background:#0f1117;border:1px solid #2d3748;border-radius:10px;padding:1rem;
      cursor:pointer;text-align:center;transition:border-color .15s,background .15s;
      text-decoration:none;display:block}
    .mode-btn:hover{border-color:#475569;background:rgba(255,255,255,.03)}
    .mode-icon{font-size:1.4rem;margin-bottom:.3rem}
    .mode-label{font-size:.85rem;font-weight:600;color:#f1f5f9}
    .mode-desc{font-size:.75rem;color:#475569;margin-top:.2rem}
    .sub-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem}
    .sub-hdr h2{font-size:1rem;color:#94a3b8}
    .user-card{display:flex;align-items:center;gap:1.2rem;padding:1.2rem 1.6rem;margin-top:0}
    .user-avatar{font-size:2.2rem;flex-shrink:0;background:#1e2433;border-radius:50%;width:3.2rem;height:3.2rem;display:flex;align-items:center;justify-content:center}
    .user-info{display:flex;flex-direction:column;gap:.25rem;min-width:0}
    .user-name{font-size:1rem;font-weight:700;color:#f1f5f9}
    .user-dept{font-size:.82rem;color:#64748b}
    .user-email{font-size:.82rem;color:#f97316;text-decoration:none;word-break:break-all}
    .user-email:hover{text-decoration:underline}
    @media(max-width:480px){
      .card{padding:1.2rem}
      .level-grid,.mode-grid{grid-template-columns:1fr}
      .result-card{padding:1.5rem}
    }
  </style>
</head>
<body>
<div class="container">
  <header>
    <h1>🔥 Atemschutz Leistungsprüfung</h1>
    {% if level %}
      <p>Trainingsquiz</p>
      <span class="level-pill {{ level }}">
        {{ '🥉 Stufe 1 – Bronze' if level == 'bronze' else ('🥈 Stufe 2 – Silber' if level == 'silver' else ('🥇 Stufe 3 – Gold' if level == 'gold' else '🎲 Random – Alle Stufen')) }}
      </span>
    {% else %}
      <p>Trainingsquiz – Stufe 1 &amp; 2</p>
    {% endif %}
  </header>
  {{ body | safe }}
</div>
</body>
</html>"""


def render(body, level=None):
    return j2(BASE, body=body, level=level)


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    body = """
<div class="card start-card">
  <div style="font-size:3rem;margin-bottom:.8rem">🧰</div>
  <h2>Wähle deine Prüfungsstufe</h2>
  <p>Klicke auf Bronze, Silber oder Gold, um die passenden Fragen zu üben.</p>
  <div class="level-grid">
    <a href="/level/bronze" class="level-card bc">
      <div class="level-icon">🥉</div>
      <div class="level-title">Bronze</div>
      <div class="level-sub">Stufe 1 · Fragen 1–30</div>
    </a>
    <a href="/level/silver" class="level-card sc">
      <div class="level-icon">🥈</div>
      <div class="level-title">Silber</div>
      <div class="level-sub">Stufe 2 · Fragen 31–60</div>
    </a>
    <a href="/level/gold" class="level-card gc">
      <div class="level-icon">🥇</div>
      <div class="level-title">Gold</div>
      <div class="level-sub">Stufe 3 · Fragen 61–100</div>
    </a>
    <a href="/start?level=all&amp;mode=shuffle" class="level-card rc">
      <div class="level-icon">🎲</div>
      <div class="level-title">Random</div>
      <div class="level-sub">Alle 100 Fragen · zufällig</div>
    </a>
  </div>
</div>
<div class="card user-card">
  <div class="user-avatar">👨‍🚒</div>
  <div class="user-info">
    <div class="user-name">Johannes Kainz</div>
    <div class="user-dept">🚒 Freiwillige Feuerwehr der Stadt Fehring</div>
    <a href="mailto:kainzjoh@icloud.com" class="user-email">kainzjoh@icloud.com</a>
  </div>
</div>"""
    return render(body)


@app.route("/level/<lv>")
def level_page(lv):
    if lv not in ("bronze", "silver", "gold"):
        return redirect(url_for("index"))
    if lv == "bronze":
        icon, title, color, ar, gr = "🥉", "Stufe 1 – Bronze", "#cd7f32", "Fragen 1–5", "Fragen 17–30"
    elif lv == "silver":
        icon, title, color, ar, gr = "🥈", "Stufe 2 – Silber", "#94a3b8", "Fragen 31–39", "Fragen 53–60"
    else:
        icon, title, color, ar, gr = "🥇", "Stufe 3 – Gold", "#eab308", "Fragen 61–69", "Fragen 70–100"
    body = j2("""
<div class="card start-card">
  <div class="level-icon">{{ icon }}</div>
  <h2 style="color:{{ color }};margin-bottom:.4rem">{{ title }}</h2>
  <p>30 Fragen aus Atmung, Gerätekunde und Allgemeine Fragen.<br>Wähle deinen Modus.</p>
  <div class="mode-grid">
    <a href="/start?level={{ lv }}&amp;mode=all" class="mode-btn">
      <div class="mode-icon">📚</div><div class="mode-label">Alle Fragen</div><div class="mode-desc">In Reihenfolge</div>
    </a>
    <a href="/start?level={{ lv }}&amp;mode=shuffle" class="mode-btn">
      <div class="mode-icon">🔀</div><div class="mode-label">Zufällig</div><div class="mode-desc">Gemischt</div>
    </a>
    <a href="/start?level={{ lv }}&amp;mode=atmung" class="mode-btn">
      <div class="mode-icon">🫁</div><div class="mode-label">Nur Atmung</div><div class="mode-desc">{{ ar }}</div>
    </a>
    <a href="/start?level={{ lv }}&amp;mode=allgemein" class="mode-btn">
      <div class="mode-icon">📋</div><div class="mode-label">Nur Allgemein</div><div class="mode-desc">{{ gr }}</div>
    </a>
  </div>
  <a href="/" class="btn btn-ghost" style="font-size:.85rem">← Zurück zur Stufenwahl</a>
</div>""", lv=lv, icon=icon, title=title, color=color, ar=ar, gr=gr)
    return render(body, level=lv)


@app.route("/start")
def start():
    lv = request.args.get("level", "bronze")
    if lv not in ("bronze", "silver", "gold"):
        return redirect(url_for("index"))
    mode = request.args.get("mode", "all")
    idxs = build_indices(lv, mode)
    session.clear()
    session["level"] = lv
    session["q_indices"] = idxs   # ← only small list of ints, never question text
    session["index"] = 0
    session["score"] = 0
    session["answers"] = []
    return redirect(url_for("quiz"))


@app.route("/quiz")
def quiz():
    qs = session_questions()
    idx = session.get("index", 0)
    lv = session.get("level", "bronze")
    if not qs or idx >= len(qs):
        return redirect(url_for("result"))
    q = qs[idx]
    hc = {"bronze":"hb","silver":"hs","gold":"hg"}.get(lv,"ha")
    body = j2("""
<div class="progress-label">
  <span>Frage {{ cur + 1 }} von {{ total }}</span>
  <span>{{ score }} richtig</span>
</div>
<div class="progress-wrap">
  <div class="progress-bar {{ lv }}" style="width:{{ pct }}%"></div>
</div>
<div class="card">
  <span class="category-badge {{ lv }}">{{ q.category }}</span>
  <div class="question-num">Frage {{ q.id }}</div>
  <div class="question-text">{{ q.question }}</div>
  <div class="options">
    {% set letters = ['a','b','c'] %}
    {% for i in range(q.options|length) %}
      {% set letter = letters[i] %}
      <button class="option {{ hc }}"
              data-correct="{{ 'true' if letter == q.correct else 'false' }}"
              data-value="{{ letter }}">
        <span class="key">{{ letter }})</span>
        <span>{{ q.options[i][3:] }}</span>
      </button>
    {% endfor %}
  </div>
  <div class="feedback" id="feedback"></div>
</div>
<form method="post" action="/answer" id="af">
  <input type="hidden" name="answer" id="ai" value="">
  <div class="nav-row">
    <a href="/restart" class="btn btn-ghost">↩ Neu starten</a>
    <div style="display:flex;gap:.6rem">
      <button type="button" id="skip-btn" class="btn btn-ghost" onclick="go('skip')">Überspringen</button>
      <button type="button" id="next-btn" class="btn btn-{{ lv }}" style="display:none" onclick="go('')">Weiter →</button>
    </div>
  </div>
</form>
<script>
document.querySelectorAll('.option').forEach(b=>{
  b.addEventListener('click',function(){
    const ok=this.dataset.correct==='true';
    document.querySelectorAll('.option').forEach(x=>{
      x.disabled=true;
      if(x.dataset.correct==='true') x.classList.add('correct');
    });
    if(!ok) this.classList.add('wrong');
    document.getElementById('ai').value=this.dataset.value;
    const fb=document.getElementById('feedback');
    fb.classList.add('show',ok?'ok':'err');
    fb.textContent=ok?'✓ Richtig!':'✗ Falsch – die richtige Antwort ist grün markiert.';
    document.getElementById('next-btn').style.display='inline-block';
    document.getElementById('skip-btn').style.display='none';
  });
});
function go(v){if(v==='skip')document.getElementById('ai').value='skip';document.getElementById('af').submit();}
</script>""",
        q=q, cur=idx, total=len(qs), score=session.get("score", 0),
        lv=lv, hc=hc, pct=int(idx / len(qs) * 100))
    return render(body, level=lv)


@app.route("/answer", methods=["POST"])
def answer():
    qs = session_questions()
    idx = session.get("index", 0)
    if idx < len(qs):
        ans = request.form.get("answer", "skip")
        if ans == qs[idx]["correct"]:
            session["score"] = session.get("score", 0) + 1
        session["answers"] = session.get("answers", []) + [ans]
        session["index"] = idx + 1
    return redirect(url_for("quiz"))


@app.route("/result")
def result():
    qs = session_questions()
    score = session.get("score", 0)
    total = len(qs)
    pct = int(score / total * 100) if total else 0
    lv = session.get("level", "bronze")
    cats = {}
    answers = session.get("answers", [])
    for i, q in enumerate(qs):
        c = q["category"]
        if c not in cats:
            cats[c] = {"score": 0, "total": 0}
        cats[c]["total"] += 1
        if i < len(answers) and answers[i] == q["correct"]:
            cats[c]["score"] += 1
    body = j2("""
<div class="card result-card">
  <div class="result-score {{ lv }}">{{ score }}/{{ total }}</div>
  <div class="result-sub">{{ pct }}% korrekt beantwortet</div>
  <div class="result-verdict {{ 'verdict-pass' if pct >= 75 else 'verdict-fail' }}">
    {{ '🎉 Bestanden!' if pct >= 75 else '❌ Nicht bestanden – weiterüben!' }}
  </div>
  <div class="category-stats">
    {% for cat, d in cats.items() %}
    <div class="cat-row">
      <span class="cat-name">{{ cat }}</span>
      <span class="cat-score">{{ d.score }}/{{ d.total }}</span>
    </div>
    {% endfor %}
  </div>
  <div style="display:flex;gap:.75rem;justify-content:center;flex-wrap:wrap">
    {% if lv == "all" %}<a href="/start?level=all&amp;mode=shuffle" class="btn btn-all">🔄 Nochmal (zufällig)</a>{% else %}<a href="/level/{{ lv }}" class="btn btn-{{ lv }}">🔄 Nochmal</a>{% endif %}
    <a href="/start?level={{ lv }}&amp;mode=shuffle" class="btn btn-ghost">🔀 Zufällig</a>
    <a href="/review?level={{ lv }}" class="btn btn-ghost">📋 Alle Antworten</a>
    <a href="/" class="btn btn-ghost">← Stufenwahl</a>
  </div>
</div>""", score=score, total=total, pct=pct, cats=cats, lv=lv)
    return render(body, level=lv)


@app.route("/review")
def review():
    lv = request.args.get("level", session.get("level", "bronze"))
    qs = ALL_QUESTIONS.get(lv, QUESTIONS_BRONZE)
    body = j2("""
<div class="sub-hdr">
  <h2>Alle Fragen &amp; richtige Antworten</h2>
  <a href="/level/{{ lv }}" class="btn btn-ghost" style="padding:.4rem .9rem;font-size:.85rem">← Zurück</a>
</div>
{% set letters = ['a','b','c'] %}
{% for q in questions %}
<div class="card" style="margin-bottom:.75rem;padding:1.2rem 1.4rem">
  <span class="category-badge {{ lv }}">{{ q.category }}</span>
  <div class="question-num">Frage {{ q.id }}</div>
  <div class="question-text" style="font-size:.95rem;margin-bottom:.8rem">{{ q.question }}</div>
  <div class="options">
    {% for i in range(q.options|length) %}
      {% set letter = letters[i] %}
      <div class="option {{ 'correct' if letter == q.correct else '' }}" style="cursor:default;padding:.65rem .9rem">
        <span class="key">{{ letter }})</span>
        <span style="font-size:.88rem">{{ q.options[i][3:] }}</span>
      </div>
    {% endfor %}
  </div>
</div>
{% endfor %}""", questions=qs, lv=lv)
    return render(body, level=lv)


@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
