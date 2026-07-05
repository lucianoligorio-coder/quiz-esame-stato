import streamlit as st
import json
import random

# Configurazione della pagina (Ottimizzata al massimo per iPhone)
st.set_page_config(
    page_title="Quiz Esame di Stato",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personalizzato per trasformare i Radio Button in grandi pulsanti touch-friendly
st.markdown("""
<style>
    /* Rende le opzioni delle crocette molto più grandi e facili da cliccare su iPhone */
    .stRadio div[role="radiogroup"] label {
        background-color: #f1f3f5 !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        display: block !important;
        border: 1px solid #e9ecef !important;
        font-size: 16px !important;
    }
    .stRadio div[role="radiogroup"] label:hover {
        background-color: #e2e6ea !important;
    }
    .stButton > button { 
        width: 100%; 
        padding: 15px !important; 
        font-size: 18px !important; 
        border-radius: 12px !important;
        background-color: #007bff !important;
        color: white !important;
        font-weight: bold !important;
    }
    h1 { font-size: 24px !important; text-align: center; font-weight: bold; }
    h3 { font-size: 18px !important; margin-top: 20px !important; }
</style>
""", unsafe_allow_html=True)

def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("File 'questions.json' non trovato nel server.")
        return None

questions_db = load_questions()

# Gestione dello stato dell'applicazione
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

st.title("📚 Simulatore Esame di Stato")

if questions_db:
    # Menu Scelta Livello
    opzioni_livello = ["Livello 1 - Fondamentali"]
    if st.session_state.livello_sbloccato >= 2:
        opzioni_livello.append("Livello 2 - Domande Complesse 🔥")
        
    livello_scelto_str = st.selectbox("Seleziona il Livello:", opzioni_livello, disabled=st.session_state.test_in_corso)
    st.session_state.livello_selezionato = 1 if "Livello 1" in livello_scelto_str else 2

    # Avvio Test
    if not st.session_state.test_in_corso:
        st.write("Clicca il pulsante sotto per generare 30 domande casuali dal tuo PDF.")
        if st.button("🚀 INIZIA NUOVO TEST"):
            chiave_livello = f"livello_{st.session_state.livello_selezionato}"
            tutte_le_domande = questions_db.get(chiave_livello, [])
            
            k_domande = min(30, len(tutte_le_domande))
            st.session_state.domande_estratte = random.sample(tutte_le_domande, k_domande)
            
            # Reset delle risposte
            st.session_state.risposte_utente = {q['id']: None for q in st.session_state.domande_estratte}
            st.session_state.test_in_corso = True
            st.session_state.mostra_risultati = False
            st.rerun()

    # Svolgimento del Quiz (Crocette sempre visibili)
    if st.session_state.test_in_corso and not st.session_state.mostra_risultati:
        st.info(f"Domande nel test: {len(st.session_state.domande_estratte)} | Massimo 4 errori consentiti.")
        
        for i, q in enumerate(st.session_state.domande_estratte):
            st.markdown(f"### **{i+1}. {q['domanda']}**")
            
            # Qui mostriamo le opzioni direttamente come pulsanti a scelta singola (senza tendine nascoste)
            opzione_selezionata = st.radio(
                label=f"Opzioni per la domanda {q['id']}",
                options=q['opzioni'],
                index=None, # Nessuna risposta preselezionata all'inizio
                key=f"radio_{q['id']}",
                label_visibility="collapsed"
            )
            
            # Registra la risposta toccata dall'utente
            if opzione_selezionata:
                st.session_state.risposte_utente[q['id']] = opzione_selezionata
        
        st.markdown("---")
        if st.button("🏁 CONSEGNA IL TEST"):
            st.session_state.mostra_risultati = True
            st.rerun()

    # Risultati finali
    if st.session_state.mostra_risultati:
        st.header("📊 Risultato del tuo Test")
        
        errori = 0
        totale_domande = len(st.session_state.domande_estratte)
        scheda_correzione = []
        
        for q in st.session_state.domande_estratte:
            risposta_data = st.session_state.risposte_utente.get(q['id'])
            risposta_esatta = q['risposta_corretta']
            
            if risposta_data is None:
                risposta_data = "Nessuna risposta data"
            
            if risposta_data != risposta_esatta:
                errori += 1
                scheda_correzione.append({
                    "domanda": q['domanda'],
                    "tua": risposta_data,
                    "corretta": risposta_esatta
                })
        
        st.metric(label="Errori Commessi", value=f"{errori} / {totale_domande}")
        
        if errori <= 4:
            st.success("🎉 SUPERATO! Ottimo lavoro.")
            if st.session_state.livello_selezionato == 1 and st.session_state.livello_sbloccato == 1:
                st.session_state.livello_sbloccato = 2
                st.info("🔓 LIVELLO 2 SBLOCCATO! Ora puoi selezionarlo dal menu in alto.")
        else:
            st.error(f"🔴 Hai commesso {errori} errori. Il limite per sbloccare il livello successivo è 4.")
            
        if errori > 0:
            st.subheader("🔍 Dove hai sbagliato:")
            for item in scheda_correzione:
                with st.expander(f"Dettaglio errore: {item['domanda'][:40]}..."):
                    st.write(f"**Domanda:** {item['domanda']}")
                    st.markdown(f"❌ La tua risposta: <span style='color:#dc3545; font-weight:bold;'>{item['tua']}</span>", unsafe_allow_html=True)
                    st.markdown(f"✅ Risposta esatta: <span style='color:#28a745; font-weight:bold;'>{item['corretta']}</span>", unsafe_allow_html=True)
        
        if st.button("🔄 Fai un altro test"):
            st.session_state.test_in_corso = False
            st.session_state.mostra_risultati = False
            st.rerun()
