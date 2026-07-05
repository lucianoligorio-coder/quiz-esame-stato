import streamlit as st
import json

# Configurazione della pagina per massima usabilità su iPhone e schermi Mobile
st.set_page_config(
    page_title="Quiz Esame di Stato Architetti",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Stile CSS per ingrandire i radio button e renderli pulsanti Touch-Friendly
st.markdown("""
<style>
    .stRadio div[role="radiogroup"] label {
        background-color: #f8f9fa !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        display: block !important;
        border: 1px solid #dee2e6 !important;
        font-size: 16px !important;
        cursor: pointer;
    }
    .stRadio div[role="radiogroup"] label:hover {
        background-color: #e9ecef !important;
    }
    .stButton > button { 
        width: 100%; 
        padding: 16px !important; 
        font-size: 18px !important; 
        border-radius: 12px !important;
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        border: none;
    }
    h1 { font-size: 24px !important; text-align: center; font-weight: bold; color: #343a40; }
    h3 { font-size: 17px !important; margin-top: 22px !important; color: #495057; }
    .schema-box {
        background-color: #1e1e1e;
        color: #39ff14;
        font-family: 'Courier New', monospace;
        padding: 14px;
        border-radius: 10px;
        white-space: pre-wrap;
        font-size: 12.5px;
        margin-bottom: 18px;
        border-left: 6px solid #007bff;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Errore nel caricamento del file questions.json: {e}")
        return None

questions_db = load_questions()

# Dichiarazione degli stati dell'applicazione per sblocco progressivo sequenziale
if "livello_sbloccato" not in st.session_state:
    st.session_state.livello_sbloccato = 1
if "test_in_corso" not in st.session_state:
    st.session_state.test_in_corso = False
if "domande_estratte" not in st.session_state:
    st.session_state.domande_estratte = []
if "risposte_utente" not in st.session_state:
    st.session_state.risposte_utente = {}
if "mostra_risultati" not in st.session_state:
    st.session_state.mostra_risultati = False
if "livello_selezionato" not in st.session_state:
    st.session_state.livello_selezionato = 1

st.markdown("<h1>📚 Simulatore Esame di Stato Architetti</h1>", unsafe_allow_html=True)

# Mappatura dei 9 moduli corrispondenti ai PDF
nomi_livelli = {
    1: "Livello 1: Normativa Utile 📐",
    2: "Livello 2: Parametri Standard Urbanistici 📊",
    3: "Livello 3: Tipologie di Strutture 🏗️",
    4: "Livello 4: Case 🏡",
    5: "Livello 5: Sanità 🏥",
    6: "Livello 6: Edifici a Destinazione Commerciale 🛍️",
    7: "Livello 7: Edifici Scolastici 🏫",
    8: "Livello 8: Edifici Contenitori 🏛️",
    9: "Livello 9: Edifici Sportivi 🏋️"
}

# Schede grafiche e di layout per lo studio visivo
schemi_grafici = {
    1: "📐 DISPOSIZIONI DISTACCHI STRADALI & ALBERI:\n+-------------------------------------------------------+\n| Larghezza Carreggiata  -->  Distanza Minima Edificio  |\n| Meno di 7,00 metri     -->  5,00 metri                |\n| Tra 7,00 e 15,00 metri -->  7,50 metri                |\n| Oltre 15,00 metri      -->  10,00 metri               |\n+-------------------------------------------------------+\n| Limiti Alberi dal Confine:                            |\n| Siepi (h<2.5m): 0.5m | Medio F.: 1.5m | Alto F.: 3.0m |\n+-------------------------------------------------------+",
    2: "📊 STANDARD RESIDENZIALI (ZONA C - Comuni >10k ab):\nQuota minima obbligatoria totale: 18 mq / abitante\n suddivisa nei seguenti sotto-blocchi funzionali:\n ├── 🏫 Istruzione (Nidi/Scuole):       4,50 mq / ab\n ├── 🌳 Verde Pubblico Attrezzato:       9,00 mq / ab\n ├── 🚗 Parcheggi Pubblici di Sosta:   2,25 mq / ab\n └── 🏛️ Attrezzature di Interesse Q.re: 2,00 mq / ab\n* Zona B: Sup. Coperta > 12.5% (1/8) SF e Densità > 1.5 mc/mq",
    3: "🏗️ PREDIMENSIONAMENTO STRUTTURALE RAPIDO:\n[ A. CALCESTRUZZO ARMATO (Luce L: 5 - 8 metri) ]\n  Altezza trave h ≈ Luce (L) / 20\n  Es: Luce 6.00 m  -->  h trave = 30 cm\n\n[ B. ACCIAIO (Profili IPE, HEA, HEB) ]\n  Altezza trave h (in mm) ≈ da 40 a 50 volte la Luce L (in metri)\n  Es: Luce 6.00 m  -->  h trave = 240 / 300 mm",
    4: "🏡 DISCIPLINARE TAGLI INTERNI (D.M. 5 LUGLIO 1975):\n+-------------------------------------------------------+\n| Abitanti alloggio | Superficie Minima Netta Richiesta |\n| 1 Persona (Mono)  | 28 mq  (Bilocale: 38 mq)          |\n| 2 Persone (Mono)  | 38 mq  (Bilocale: 42 mq)          |\n| 3 Persone         | da 42 mq a 56 mq                  |\n| 4 Persone         | da 56 mq a 66 mq                  |\n| 5 Persone         | da 66 mq a 76 mq                  |\n| 6 Persone         | da 76 mq a 86 mq                  |\n+-------------------------------------------------------+",
    5: "🏥 REPARTI DI DEGENZA (PIANO TIPO OSPEDALIERO):\n+-------------------------------------------------------+\n|               CAMERE DI DEGENZA (Singole/Doppie)      |\n|               Min. 6 mq per persona / min. totale 9 mq|\n+================== Parete Divisoria ===================+\n|  ◀── Corridoio Centrale di Distribuzione: MIN 3.5m ──▶|\n+================== Parete Divisoria ===================+\n|   Infermieria (29mq) | Sale Medici/Visite Ospedale    |\n+-------------------------------------------------------+",
    6: "🛍️ STRUTTURE COMMERCIALI AL DETTAGLIO (Comuni >10k ab):\n ├── 🛒 Esercizi di Vicinato:    Fino a 250 mq superficie vendita\n ├── 🏪 Medie Strutture Vendita: Da 251 mq a 2500 mq\n └── 🏢 Grandi Strutture Vendita: Oltre 2500 mq\n* Altezza Utile interna minima dei Negozi ordinari = 3,20 m\n* Chioschi: Area min 15-20 mq, banco h 120 cm con appoggio >30cm",
    7: "🏫 PARAMETRI EDILIZIA SCOLASTICA (D.M. 18/12/1975):\n ├── 💨 Rapporto Aeroilluminante (RAI) nelle Aule: MIN 1/5\n ├── 📏 Altezza minima interna aule didattiche:   3,00 metri\n ├── 👦 Elementari e Medie (Superficie netta):    1,80 mq/alunno\n └── 🧑 Scuole Superiori (Superficie netta):      1,96 mq/alunno\n* Distacco da altri edifici: 12 metri o 4/3 dell'altezza del vicino",
    8: "🏛️ EDIFICI CONTENITORI & COMPLESSO CIMITERIALE:\n ├── ⚰️ Fascia di rispetto Piccoli Comuni:  50 metri\n ├── 📐 Fascia di rispetto Ampliamenti:    100 metri\n └── 🏢 Fascia di rispetto Grandi Comuni:   200 metri\n* Sala Conferenze: 1,5-2 mq / persona | Vol: 4-8 mc / persona\n* Panche Chiesa: Corridoio centrale pulito largo min 1,50 m",
    9: "🏋️ STRUTTURE SPORTIVE - PROPORZIONI E DIMENSIONI:\n ├── 📂 Relazioni d'Area Nuclei: Atrio > 1/25 | Magazzino: 1/10\n ├── 🏐 Campo Pallavolo:       15 x 24 metri\n ├── 🏀 Campo Basket:          18 x 30 metri\n ├── 🎾 Campo Tennis Esterno:  18,27 x 36,57 metri\n └── 🏊 Vasca Olimpica Corta:  25 x 13 metri (Prof: 90-180 cm)\n└── 🏊 Vasca Olimpica Lunga:  50 x 21,25 metri (10-12 corsie)"
}

if questions_db:
    # Generazione automatica delle opzioni del menu basata sui livelli sbloccati
    opzioni_livello = []
    for liv in range(1, st.session_state.livello_sbloccato + 1):
        if liv in nomi_livelli:
            opzioni_livello.append(nomi_livelli[liv])
            
    livello_scelto_str = st.selectbox("Seleziona il modulo d'esame:", opzioni_livello, disabled=st.session_state.test_in_corso)
    
    for num, nome in nomi_livelli.items():
        if nome == livello_scelto_str:
            st.session_state.livello_selezionato = num

    # Schermata iniziale: Visualizzazione dello schema grafico didattico
    if not st.session_state.test_in_corso:
        st.markdown("### 👁️ Tavola Sinottica / Schema di Riferimento del PDF:")
        st.markdown(f'<div class="schema-box">{schemi_grafici.get(st.session_state.livello_selezionato, "Nessuno schema caricato.")}</div>', unsafe_allow_html=True)
        
        st.write("Verranno estratte tutte le **15 domande complete** contenute all'interno del modulo selezionato. Per passare il livello devi fare meno di 4 errori.")
        
        if st.button("🚀 AVVIA SIMULAZIONE COMPLETA (15 DOMANDE)"):
            chiave_livello = f"livello_{st.session_state.livello_selezionato}"
            st.session_state.domande_estratte = questions_db.get(chiave_livello, [])
            
            st.session_state.risposte_utente = {q['id']: None for q in st.session_state.domande_estratte}
            st.session_state.test_in_corso = True
            st.session_state.mostra_risultati = False
            st.rerun()

    # Svolgimento attivo del quiz
    if st.session_state.test_in_corso and not st.session_state.mostra_risultati:
        st.info(f"📋 Stai rispondendo alle 15 domande del modulo. Rispondi con cura!")
        
        for i, q in enumerate(st.session_state.domande_estratte):
            st.markdown(f"### **{i+1}. {q['domanda']}**")
            
            opzione_selezionata = st.radio(
                label=f"Q_{q['id']}",
                options=q['opzioni'],
                index=None,
                key=f"radio_{q['id']}",
                label_visibility="collapsed"
            )
            
            if opzione_selezionata:
                st.session_state.risposte_utente[q['id']] = opzione_selezionata
                
        st.markdown("---")
        if st.button("🏁 TERMINA LA PROVA E CORREGGI"):
            st.session_state.mostra_risultati = True
            st.rerun()

    # Elaborazione degli esiti e calcolo degli sblocchi sequenziali
    if st.session_state.mostra_risultati:
        st.header("📊 Resoconto della prova")
        
        errori = 0
        totale_domande = len(st.session_state.domande_estratte)
        scheda_correzione = []
        
        for q in st.session_state.domande_estratte:
            risposta_data = st.session_state.risposte_utente.get(q['id'])
            risposta_esatta = q['risposta_corretta']
            
            if risposta_data is None:
                risposta_data = "Nessuna risposta fornita"
                
            if risposta_data != risposta_esatta:
                errori += 1
                scheda_correzione.append({
                    "domanda": q['domanda'],
                    "tua": risposta_data,
                    "corretta": risposta_esatta
                })
                
        st.metric(label="Errori Commessi", value=f"{errori} / {totale_domande}")
        
        if errori <= 4:
            st.success("🎉 MODULO COMPLETATO CON SUCCESSO!")
            if st.session_state.livello_selezionato == st.session_state.livello_sbloccato:
                if st.session_state.livello_sbloccato < 9:
                    st.session_state.livello_sbloccato += 1
                    st.info(f"🔓 SBLOCCATO: {nomi_livelli[st.session_state.livello_sbloccato]}! Selezionalo ora nel menu a tendina.")
                else:
                    st.balloons()
                    st.success("🏆 ECCELLENTE! Hai completato l'intero percorso di studio sbloccando tutti i 9 moduli d'esame!")
        else:
            st.error(f"🔴 Livello non superato. Hai commesso {errori} errori (il massimo consentito è 4). Rivedi lo schema tecnico e riprova!")
            
        if errori > 0:
            st.subheader("🔍 Analisi dettagliata degli errori:")
            for item in scheda_correzione:
                with st.expander(f"Errore: {item['domanda'][:50]}..."):
                    st.write(f"**Quesito:** {item['domanda']}")
                    st.markdown(f"❌ La tua risposta: <span style='color:#dc3545; font-weight:bold;'>{item['tua']}</span>", unsafe_allow_html=True)
                    st.markdown(f"✅ Disposto di legge/Dato corretto: <span style='color:#28a745; font-weight:bold;'>{item['corretta']}</span>", unsafe_allow_html=True)
                    
        if st.button("🔄 Ritorna alla selezione dei PDF"):
            st.session_state.test_in_corso = False
            st.session_state.mostra_risultati = False
            st.rerun()
