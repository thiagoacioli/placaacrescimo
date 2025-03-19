import streamlit as st
import re
from datetime import datetime, timedelta

def parse_time(time_str):
    """Converte string de tempo (MM:SS) para segundos."""
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds
    except:
        return None

def extract_events(text, language="pt"):
    """Extrai eventos relevantes do texto."""
    events = []
    
    # Definir padrões de regex baseados no idioma
    if language == "pt":
        # Padrão para português
        time_pattern = r'(\d{1,2}:\d{2})'
        foul_keywords = ['falta', 'tiro livre', 'free kick']
        sub_keywords = ['substituição', 'substituicao', 'troca']
    else:
        # Padrão para inglês
        time_pattern = r'(\d{1,2}:\d{2})'
        foul_keywords = ['foul', 'free kick']
        sub_keywords = ['substitution', 'sub']
    
    # Separar o texto em linhas
    lines = text.lower().split('\n')
    
    for line in lines:
        # Encontrar todos os horários na linha
        times = re.findall(time_pattern, line)
        
        if times:
            event_time = times[0]
            event_seconds = parse_time(event_time)
            
            if event_seconds is not None:
                # Verificar se é um evento prioritário
                is_foul = any(keyword in line.lower() for keyword in foul_keywords)
                is_sub = any(keyword in line.lower() for keyword in sub_keywords)
                
                # Calcular duração estimada
                duration = 0
                if is_foul:
                    duration = 30  # 30 segundos para faltas
                elif is_sub:
                    duration = 45  # 45 segundos para substituições
                
                if duration > 0:
                    events.append({
                        'time': event_time,
                        'seconds': event_seconds,
                        'type': 'foul' if is_foul else 'substitution',
                        'duration': duration,
                        'text': line.strip()
                    })
    
    return events

def main():
    st.title("⚽ Calculadora de Tempo de Paralisação")
    
    # Seleção de idioma
    language = st.radio("Selecione o idioma dos eventos:", ["Português", "Inglês"], horizontal=True)
    lang_code = "pt" if language == "Português" else "en"
    
    # Área de texto para input dos eventos
    st.subheader("Eventos da Partida")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Primeiro Tempo")
        first_half_events = st.text_area(
            "Cole os eventos do primeiro tempo aqui",
            height=300,
            key="first_half"
        )
    
    with col2:
        st.write("Segundo Tempo")
        second_half_events = st.text_area(
            "Cole os eventos do segundo tempo aqui",
            height=300,
            key="second_half"
        )
    
    if st.button("Calcular Tempo de Paralisação"):
        # Extrair eventos
        first_half = extract_events(first_half_events, lang_code)
        second_half = extract_events(second_half_events, lang_code)
        
        # Calcular tempo total
        first_half_stoppage = sum(event['duration'] for event in first_half)
        second_half_stoppage = sum(event['duration'] for event in second_half)
        total_stoppage = first_half_stoppage + second_half_stoppage
        
        # Exibir resultados
        st.subheader("Resultado")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Tempo de Paralisação (1º Tempo)", f"{first_half_stoppage // 60}:{first_half_stoppage % 60:02d}")
        
        with col2:
            st.metric("Tempo de Paralisação (2º Tempo)", f"{second_half_stoppage // 60}:{second_half_stoppage % 60:02d}")
        
        with col3:
            st.metric("Tempo Total de Paralisação", f"{total_stoppage // 60}:{total_stoppage % 60:02d}")
        
        # Exibir detalhes dos eventos
        st.subheader("Detalhes dos Eventos")
        
        st.write("Primeiro Tempo:")
        if first_half:
            for event in first_half:
                st.write(f"⏱️ {event['time']} - {event['text']} - Paralisação: {event['duration']} segundos")
        else:
            st.write("Nenhum evento de paralisação encontrado.")
        
        st.write("Segundo Tempo:")
        if second_half:
            for event in second_half:
                st.write(f"⏱️ {event['time']} - {event['text']} - Paralisação: {event['duration']} segundos")
        else:
            st.write("Nenhum evento de paralisação encontrado.")

if __name__ == "__main__":
    main()
