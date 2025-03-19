import streamlit as st
import re
import pandas as pd

def extract_events(text, language='pt'):
    """Extrai eventos do texto fornecido, identificando tempos e tipos de eventos."""
    events = []
    
    # Definir padrões de expressão regular para encontrar eventos
    if language == 'pt':
        # Padrão para português: tempo + tipo de evento
        pattern = r'(\d+)[\'|\′]?\s+([\w\s]+)'
        
        # Palavras-chave para eventos importantes em português
        priority_keywords = {
            'alta': ['livre', 'falta', 'substituição', 'substituicao', 'subst', 'lesão', 'lesao', 'var', 'revisão', 'revisao'],
            'média': ['cartão', 'cartao', 'amarelo', 'vermelho', 'escanteio', 'tiro de meta'],
            'baixa': ['início', 'inicio', 'fim', 'gol', 'bola rolando']
        }
    else:
        # Padrão para inglês: tempo + tipo de evento
        pattern = r'(\d+)[\'|\′]?\s+([\w\s]+)'
        
        # Palavras-chave para eventos importantes em inglês
        priority_keywords = {
            'alta': ['free kick', 'foul', 'substitution', 'sub', 'injury', 'var', 'review'],
            'média': ['card', 'yellow', 'red', 'corner', 'goal kick'],
            'baixa': ['start', 'end', 'goal', 'ball in play']
        }
    
    # Encontrar todos os matches no texto
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    for match in matches:
        time = int(match[0])
        event_type = match[1].strip()
        
        # Determinar prioridade do evento
        priority = 'baixa'
        for p, keywords in priority_keywords.items():
            if any(keyword in event_type.lower() for keyword in keywords):
                priority = p
                break
        
        events.append({
            'tempo': time,
            'evento': event_type,
            'prioridade': priority
        })
    
    return events

def calculate_stoppage_time(events, half_duration=45):
    """Calcula o tempo de paralisação com base nos eventos."""
    if not events:
        return 0
    
    # Ordenar eventos por tempo
    events_sorted = sorted(events, key=lambda x: x['tempo'])
    
    # Calcular tempo médio de paralisação por tipo de prioridade
    stoppages = {
        'alta': 60,  # Em segundos (1 minuto para eventos de alta prioridade)
        'média': 30,  # Em segundos (30 segundos para eventos de média prioridade)
        'baixa': 15   # Em segundos (15 segundos para eventos de baixa prioridade)
    }
    
    total_stoppage_seconds = 0
    for event in events_sorted:
        if event['tempo'] <= half_duration:
            total_stoppage_seconds += stoppages[event['prioridade']]
    
    # Converter para minutos
    return total_stoppage_seconds / 60

def main():
    st.title("⚽ Calculadora de Tempo de Paralisação")
    
    # Seleção de idioma
    language = st.radio("Selecione o idioma dos eventos:", ["Português", "English"])
    lang_code = 'pt' if language == "Português" else 'en'
    
    # Área de texto para entrada de eventos
    if lang_code == 'pt':
        st.subheader("Eventos da Partida")
        event_text = st.text_area(
            "Cole aqui os eventos da partida no formato: '15' Falta para o time A, '23' Substituição time B, etc.", 
            height=200
        )
    else:
        st.subheader("Match Events")
        event_text = st.text_area(
            "Paste the match events here in the format: '15' Free kick for team A, '23' Substitution team B, etc.", 
            height=200
        )
    
    # Cálculo do tempo de paralisação
    if st.button("Calcular Tempo de Paralisação" if lang_code == 'pt' else "Calculate Stoppage Time"):
        if event_text:
            events = extract_events(event_text, lang_code)
            
            # Separar eventos por tempo (primeiro tempo e segundo tempo)
            first_half_events = [e for e in events if e['tempo'] <= 45]
            second_half_events = [e for e in events if e['tempo'] > 45]
            
            # Calcular tempo de paralisação para cada tempo
            first_half_stoppage = calculate_stoppage_time(first_half_events)
            second_half_stoppage = calculate_stoppage_time(second_half_events)
            total_stoppage = first_half_stoppage + second_half_stoppage
            
            # Exibir resultados
            st.subheader("Resultados:" if lang_code == 'pt' else "Results:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("1º Tempo" if lang_code == 'pt' else "1st Half", f"{first_half_stoppage:.1f} min")
            with col2:
                st.metric("2º Tempo" if lang_code == 'pt' else "2nd Half", f"{second_half_stoppage:.1f} min")
            with col3:
                st.metric("Total" if lang_code == 'pt' else "Total", f"{total_stoppage:.1f} min")
            
            # Mostrar eventos em uma tabela
            st.subheader("Detalhes dos Eventos:" if lang_code == 'pt' else "Event Details:")
            
            df = pd.DataFrame(events)
            df.columns = ['Tempo', 'Evento', 'Prioridade'] if lang_code == 'pt' else ['Time', 'Event', 'Priority']
            
            # Marcar eventos de alta prioridade
            def highlight_priority(row):
                priority = row['Prioridade'] if lang_code == 'pt' else row['Priority']
                if priority == 'alta':
                    return ['background-color: #ffcccc'] * len(row)
                return [''] * len(row)
            
            styled_df = df.style.apply(highlight_priority, axis=1)
            st.dataframe(styled_df)
            
            # Resumo por tipo de evento
            st.subheader("Resumo por Prioridade:" if lang_code == 'pt' else "Summary by Priority:")
            priority_counts = df['Prioridade'].value_counts() if lang_code == 'pt' else df['Priority'].value_counts()
            st.bar_chart(priority_counts)
        else:
            st.warning("Por favor, insira os eventos da partida." if lang_code == 'pt' else "Please enter match events.")

if __name__ == "__main__":
    main()
