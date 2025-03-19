import streamlit as st
import re
from datetime import datetime, timedelta

def extract_events(text, language="pt"):
    # Definindo padrões de eventos para português e inglês
    if language == "pt":
        # Padrão para detectar eventos em português
        pattern = r"(\d+:\d+)\s+(.*?)(?=\n\d+:\d+|\Z)"
        priority_events = ["livre", "falta", "substituição", "substituicao", "cartão", "cartao", "lesão", "lesao"]
    else:
        # Padrão para detectar eventos em inglês
        pattern = r"(\d+:\d+)\s+(.*?)(?=\n\d+:\d+|\Z)"
        priority_events = ["free kick", "foul", "substitution", "card", "injury"]
    
    events = []
    
    # Encontrar todos os eventos no texto
    matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
    
    for time_str, description in matches:
        # Converter o tempo para objeto datetime para facilitar cálculos
        time_obj = datetime.strptime(time_str, "%M:%S")
        
        # Verificar se é um evento prioritário
        is_priority = any(event.lower() in description.lower() for event in priority_events)
        
        # Estimar tempo de paralisação com base no tipo de evento
        stoppage_time = 0
        if is_priority:
            if any(event in description.lower() for event in ["substituição", "substituicao", "substitution"]):
                stoppage_time = 30  # 30 segundos para substituições
            elif any(event in description.lower() for event in ["livre", "falta", "free kick", "foul"]):
                stoppage_time = 45  # 45 segundos para faltas
            elif any(event in description.lower() for event in ["lesão", "lesao", "injury"]):
                stoppage_time = 60  # 60 segundos para lesões
            elif any(event in description.lower() for event in ["cartão", "cartao", "card"]):
                stoppage_time = 20  # 20 segundos para cartões
            else:
                stoppage_time = 15  # Tempo padrão para outros eventos prioritários
        
        minute = time_obj.minute + time_obj.second / 60
        half = 1 if minute <= 45 else 2
        
        events.append({
            "time": time_str,
            "description": description.strip(),
            "is_priority": is_priority,
            "stoppage_time": stoppage_time,
            "half": half
        })
    
    return events

def calculate_stoppage_time(events):
    first_half = sum(event["stoppage_time"] for event in events if event["half"] == 1)
    second_half = sum(event["stoppage_time"] for event in events if event["half"] == 2)
    
    # Converter segundos para minutos e segundos
    first_half_min, first_half_sec = divmod(first_half, 60)
    second_half_min, second_half_sec = divmod(second_half, 60)
    total_min, total_sec = divmod(first_half + second_half, 60)
    
    return {
        "first_half": f"{int(first_half_min)}:{int(first_half_sec):02d}",
        "second_half": f"{int(second_half_min)}:{int(second_half_sec):02d}",
        "total": f"{int(total_min)}:{int(total_sec):02d}"
    }

def main():
    st.title("⚽ Calculadora de Tempo de Paralisação")
    
    # Seleção de idioma
    language = st.radio(
        "Selecione o idioma dos eventos / Select language for events:",
        ("Português", "English")
    )
    
    lang_code = "pt" if language == "Português" else "en"
    
    # Área de entrada de texto
    input_label = "Cole os eventos da partida aqui:" if lang_code == "pt" else "Paste match events here:"
    events_text = st.text_area(input_label, height=300)
    
    # Exemplos para ajudar o usuário
    with st.expander("Ver exemplos de formato / See format examples"):
        if lang_code == "pt":
            st.markdown("""
            ```
            05:20 Falta de jogador A
            12:45 Substituição do jogador B pelo jogador C
            23:10 Cartão amarelo para jogador D
            31:05 Cobrança de escanteio
            44:30 Lesão do jogador E
            47:20 Livre direto para equipe local
            ```
            """)
        else:
            st.markdown("""
            ```
            05:20 Foul by player A
            12:45 Substitution of player B for player C
            23:10 Yellow card for player D
            31:05 Corner kick
            44:30 Injury of player E
            47:20 Free kick for home team
            ```
            """)
    
    if st.button("Calcular Tempo de Paralisação" if lang_code == "pt" else "Calculate Stoppage Time"):
        if events_text:
            events = extract_events(events_text, lang_code)
            stoppage_times = calculate_stoppage_time(events)
            
            # Exibir resultados
            st.subheader("Resultados" if lang_code == "pt" else "Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("1º Tempo" if lang_code == "pt" else "1st Half", stoppage_times["first_half"])
            col2.metric("2º Tempo" if lang_code == "pt" else "2nd Half", stoppage_times["second_half"])
            col3.metric("Total", stoppage_times["total"])
            
            # Exibir eventos detectados
            st.subheader("Eventos detectados" if lang_code == "pt" else "Detected Events")
            for event in events:
                if event["is_priority"]:
                    st.markdown(f"⏱️ **{event['time']}** - {event['description']} - *+{event['stoppage_time']} segundos*")
                else:
                    st.text(f"{event['time']} - {event['description']}")
        else:
            st.warning("Por favor, insira os eventos da partida" if lang_code == "pt" else "Please input match events")

if __name__ == "__main__":
    main()
