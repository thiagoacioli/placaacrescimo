import streamlit as st
import re
from datetime import datetime, timedelta

def parse_event_time(time_str):
    """Converte o tempo do evento em minutos."""
    if "+" in time_str:
        base_time, added_time = time_str.split("+")
        return int(base_time) + int(added_time)
    return int(time_str)

def extract_events(text, language):
    """Extrai eventos e tempos associados do texto inserido."""
    events = []
    
    # Padrões para cada idioma
    patterns = {
        'pt': [
            r'(\d+)(?:\+\d+)?\'\s*[-–:]?\s*(Cartão amarelo|Cartão vermelho|Substituição|Gol|Pênalti|Falta|Lesão|VAR|Atendimento médico)',
            r'(\d+)(?:\+\d+)?\'\s*[-–:]?\s*(Pausa|Parada|Interrupção)',
            r'(\d+)(?:\+\d+)?\'\s*[-–:]?\s*(Jogo parado por|Pausa para|Revisão do VAR)',
            r'(\d+)(?:\+\d+)?\'\s*[-–:]?\s*(.*)(parado|parada|interrompido)'
        ],
        'en': [
            r'(\d+)(?:\+\d+)?\'\s*[-–:]?\s*(Yellow card|Red card|Substitution|Goal|Penalty|Foul|Injury|VAR|Medical attention)',
            r'(\d+)(?:\+\d+)?\'\s*[-–:]?\s*(Break|Stop|Interruption)',
            r'(\d+)(?:\+\d+)?\'\s*[-–:]?\s*(Game stopped for|Pause for|VAR review)',
            r'(\d+)(?:\+\d+)?\'\s*[-–:]?\s*(.*)(stopped|paused|interrupted)'
        ]
    }
    
    # Eventos que geralmente resultam em jogo parado
    stoppage_events = {
        'pt': ['Cartão amarelo', 'Cartão vermelho', 'Substituição', 'Lesão', 'VAR', 
               'Atendimento médico', 'Pausa', 'Parada', 'Interrupção', 'Jogo parado', 'Revisão do VAR'],
        'en': ['Yellow card', 'Red card', 'Substitution', 'Injury', 'VAR', 
               'Medical attention', 'Break', 'Stop', 'Interruption', 'Game stopped', 'VAR review']
    }
    
    # Duração estimada de cada tipo de evento (em segundos)
    event_durations = {
        'Cartão amarelo': 30, 'Yellow card': 30,
        'Cartão vermelho': 60, 'Red card': 60,
        'Substituição': 45, 'Substitution': 45,
        'Gol': 60, 'Goal': 60,
        'Pênalti': 90, 'Penalty': 90,
        'Falta': 30, 'Foul': 30,
        'Lesão': 120, 'Injury': 120,
        'VAR': 180, 'VAR': 180,
        'Atendimento médico': 120, 'Medical attention': 120,
        'Pausa': 60, 'Break': 60,
        'Parada': 60, 'Stop': 60,
        'Interrupção': 60, 'Interruption': 60,
        'Jogo parado': 60, 'Game stopped': 60,
        'Revisão do VAR': 180, 'VAR review': 180
    }
    
    lines = text.strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
            
        for pattern in patterns[language]:
            matches = re.search(pattern, line)
            if matches:
                time_str = matches.group(1).strip()
                event_type = matches.group(2).strip()
                
                # Verifica se é um evento que normalmente causa parada
                is_stoppage = False
                for stoppage in stoppage_events[language]:
                    if stoppage.lower() in line.lower():
                        is_stoppage = True
                        break
                
                if is_stoppage:
                    # Determina a duração baseada no tipo de evento
                    duration = 30  # Default
                    for event_key, event_duration in event_durations.items():
                        if event_key.lower() in line.lower():
                            duration = event_duration
                            break
                    
                    minute = parse_event_time(time_str)
                    events.append((minute, event_type, duration))
                
                break
    
    return events

def calculate_stoppage_time(events):
    """Calcula o tempo parado em cada tempo."""
    first_half_events = [event for event in events if event[0] <= 45]
    second_half_events = [event for event in events if event[0] > 45]
    
    first_half_stoppage = sum(event[2] for event in first_half_events)
    second_half_stoppage = sum(event[2] for event in second_half_events)
    
    return first_half_stoppage, second_half_stoppage

def format_time(seconds):
    """Formata os segundos em minutos e segundos."""
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}min {seconds}s"

def main():
    st.title("⚽ Calculadora de Tempo Parado em Partidas de Futebol")
    
    st.markdown("""
    Este aplicativo calcula quanto tempo o jogo ficou parado durante o primeiro e segundo tempo de uma partida de futebol.
    """)
    
    # Seleção de idioma
    language = st.radio("Selecione o idioma dos eventos:", ["pt", "en"], format_func=lambda x: "Português" if x == "pt" else "English")
    
    # Exemplos de entrada
    examples = {
        "pt": """5' - Cartão amarelo para Neymar
12' - Substituição: Entrada de Jesus, saída de Firmino
24' - Lesão: Atendimento médico para Richarlison
31' - VAR: Revisão de possível pênalti
43' - Gol para Brasil
52' - Jogo parado por confusão na torcida
67' - Cartão vermelho para Casemiro
73' - Substituição dupla: Entram Vini Jr e Paquetá
78' - VAR: Revisão de possível impedimento
89' - Atendimento médico para Marquinhos""",
        "en": """5' - Yellow card for Neymar
12' - Substitution: Jesus in, Firmino out
24' - Injury: Medical attention for Richarlison
31' - VAR: Review of possible penalty
43' - Goal for Brazil
52' - Game stopped due to crowd trouble
67' - Red card for Casemiro
73' - Double substitution: Vini Jr and Paquetá in
78' - VAR: Review of possible offside
89' - Medical attention for Marquinhos"""
    }
    
    st.subheader("Insira os eventos da partida")
    st.write("Cada evento deve estar em uma linha separada com o tempo em minutos seguido por uma descrição do evento.")
    
    # Botão para carregar exemplo
    if st.button("Carregar exemplo"):
        events_text = examples[language]
    else:
        events_text = ""
    
    events_text = st.text_area("Eventos:", value=events_text, height=300)
    
    if st.button("Calcular Tempo Parado"):
        if events_text:
            events = extract_events(events_text, language)
            
            # Exibe os eventos encontrados
            if events:
                st.subheader("Eventos detectados que causaram parada:")
                for minute, event_type, duration in events:
                    st.write(f"{minute}' - {event_type} ({format_time(duration)})")
                
                # Calcula o tempo parado
                first_half, second_half = calculate_stoppage_time(events)
                total_stoppage = first_half + second_half
                
                st.subheader("Resultado:")
                st.write(f"⏱️ Tempo parado no primeiro tempo: **{format_time(first_half)}**")
                st.write(f"⏱️ Tempo parado no segundo tempo: **{format_time(second_half)}**")
                st.write(f"⏱️ Tempo total parado: **{format_time(total_stoppage)}**")
                
                # Representa o tempo parado visualmente
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Primeiro tempo")
                    st.progress(min(first_half / 600, 1.0))
                with col2:
                    st.subheader("Segundo tempo")
                    st.progress(min(second_half / 600, 1.0))
                
                # Sugestão de acréscimos
                first_half_added = round(first_half / 60)
                second_half_added = round(second_half / 60)
                st.subheader("Sugestão de acréscimos:")
                st.write(f"Primeiro tempo: +{first_half_added} minutos")
                st.write(f"Segundo tempo: +{second_half_added} minutos")
            else:
                st.warning("Nenhum evento que causa parada foi detectado. Verifique o formato dos eventos ou o idioma selecionado.")
        else:
            st.warning("Por favor, insira os eventos da partida.")

if __name__ == "__main__":
    main()
