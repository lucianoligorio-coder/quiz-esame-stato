import streamlit as st
import json
import random

# Configurazione della pagina (Ottimizzata per visualizzazione Mobile/iPhone)
st.set_page_config(
    page_title="Esame di Stato Quiz",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Stile CSS personalizzato per rendere i pulsanti e i testi grandi e facilmente cliccabili su iPhone
st.markdown("""
<style>
    .stRadio > div { padding: 10px; background-color: #f9f9f9; border-radius: 10px; margin-bottom: 10px; }
    .stButton > button { width: 100%; padding: 12px; font-size: 18px !important; border-radius: 8px; }
    h1 { font-size: 26px !important; text-align: center; }
    h3 { font-size: 18px !important; }
</style>
""", unsafe_allow_html=True)

# 1. Caricamento database domande
def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("File 'questions.json' non trovato! Assicurati che sia nella stessa cartella di app.py.")
        return None

questions_db = load_questions()

# 2. Inizializzazione dello Stato della Sessione (per non perdere i dati al click su iPhone)
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
    # Selezione del livello (Il livello 2 compare solo se sbloccato)
    opzioni_livello = ["Livello 1 - Fondamentali"]
    if st.session_state.livello_sbloccato >= 2:
        opzioni_livello.append("Livello 2 - Domande Complesse 🔥")
        
    livello_scelto_str = st.selectbox("Seleziona il Livello di studio:", opzioni_livello, disabled=st.session_state.test_in_corso)
    livello_scelto = 1 if "Livello 1" in livello_scelto_str else 2
    st.session_state.livello_selezionato = livello_scelto

    # Pulsante per Avviare il Test
    if not st.session_state.test_in_corso:
        if st.button("🚀 INIZIA NUOVO TEST (30 Domande Casuali)"):
            chiave_livello = f"livello_{livello_scelto}"
            tutte_le_domande = questions_db.get(chiave_livello, [])
            
            # Estrazione di massimo 30 domande casuali e uniche
            k_domande = min(30, len(tutte_le_domande))
            st.session_state.domande_estratte = random.sample(tutte_le_domande, k_domande)
            
            st.session_state.risposte_utente = {}
            st.session_state.test_in_corso = True
            st.session_state.mostra_risultati = False
            st.rerun()

    # Svolgimento del Test
    if st.session_state.test_in_corso and not st.session_state.mostra_risultati:
        st.warning(f"Test avviato: {len(st.session_state.domande_estratte)} domande estratte casualmente.")
        
        # Mostra le domande una sotto l'altra (perfetto per lo scroll verticale su iPhone)
        for i, q in enumerate(st.session_state.domande_estratte):
            st.markdown(f"### **{i+1}. {q['domanda']}**")
            
            # Mantiene traccia della risposta selezionata dall'utente
            chiave_risposta = f"q_{q['id']}"
            opzioni = q['opzioni']
            
            # Selezione risposta
            risposta = st.radio(
                "Scegli una risposta:", 
                options=["Seleziona una risposta..."] + opzioni, 
                key=chiave_risposta,
                label_visibility="collapsed"
            )
            if risposta != "Seleziona una risposta...":
                st.session_state.risposte_utente[q['id']] = risposta
        
        st.markdown("---")
        if st.button("🏁 CONSEGNA IL TEST"):
            st.session_state.mostra_risultati = True
            st.rerun()

    # Schermata dei Risultati e Correzione
    if st.session_state.mostra_risultati:
        st.header("📊 Risultato del tuo Test")
        
        errori = 0
        totale_domande = len(st.session_state.domande_estratte)
        
        scheda_correzione = []
        
        for q in st.session_state.domande_estratte:
            risposta_data = st.session_state.risposte_utente.get(q['id'], "Nessuna risposta data")
            risposta_esatta = q['risposta_corretta']
            
            if risposta_data != risposta_esatta:
                errori += 1
                scheda_correzione.append({
                    "domanda": q['domanda'],
                    "tua": risposta_data,
                    "corretta": risposta_esatta
                })
        
        # Calcolo dell'esito
        st.metric(label="Numero di Errori Commessi", value=f"{errori} / {totale_domande}")
        
        if errori <= 4:
            st.success("🎉 COMPLIMENTI! Hai superato il test con meno di 4 errori!")
            if st.session_state.livello_selezionato == 1 and st.session_state.livello_sbloccato == 1:
                st.session_state.livello_sbloccato = 2
                st.info("🔓 HAI SBLOCCATO IL LIVELLO 2 CON DOMANDE PIÙ COMPLESSE!")
        else:
            st.error(f"🔴 Non superato. Hai fatto {errori} errori (Il massimo consentito è 4). Riprova per sbloccare il livello successivo.")
            
        # Sezione di Correzione degli Errori
        if errori > 0:
            st.subheader("🔍 Riepilogo degli errori commessi:")
            for item in scheda_correzione:
                with st.expander(f"❌ Errore nella domanda: {item['domanda'][:50]}..."):
                    st.write(f"**Domanda intera:** {item['domanda']}")
                    st.markdown(f" La tua risposta: <span style='color:red'>{item['tua']}</span>", unsafe_allow_html=True)
                    st.markdown(f" Risposta corretta: <span style='color:green'>{item['corretta']}</span>", unsafe_allow_html=True)
        
        if st.button("🔄 Torna al Menu Principale / Fai un altro Test"):
            st.session_state.test_in_corso = False
            st.session_state.mostra_risultati = False
            st.rerun()
