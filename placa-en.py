import streamlit as st
import re

st.title('Calculadora de Tempo Parado no Futebol ⚽')

# Seleção de idioma
language = st.radio('Selecione o idioma dos eventos:', ['Português', 'Inglês'])

# Área para colar os eventos
events_input = st.text_area('Cole os eventos da partida aqui:', height=300, 
                           help='Exemplo:\n10\'34\'\'Dangerous Attack...\n09\'13\'\'Substitution...')

if st.button('Calcular Tempo Parado'):
    events = []
    pattern = re.compile(r"^(\d+)'(\d+)''\s*(.*)")
    
    # Palavras-chave para tempo parado
    if language == 'Inglês':
        keywords = ['substitution', 'free kick', 'throw-in']
    else:
        keywords = ['substituição', 'livre', 'lançamento lateral']
    
    # Processamento dos eventos
    for line in events_input.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        match = pattern.match(line)
        if not match:
            st.error(f'Formato inválido: "{line}"')
            continue
            
        minutos = int(match.group(1))
        segundos = int(match.group(2))
        total_segundos = minutos * 60 + segundos
        descricao = match.group(3).lower()
        
        # Verifica se é um evento de tempo parado
        is_parado = any(descricao.startswith(palavra.lower()) for palavra in keywords)
        
        # Determina o tempo
        tempo = 'primeiro' if total_segundos <= 2700 else 'segundo'  # 2700s = 45min
        
        events.append({
            'tempo': tempo,
            'segundos': total_segundos,
            'parado': is_parado
        })
    
    # Cálculo do tempo parado
    resultados = {'primeiro': 0, 'segundo': 0}
    
    for tempo in ['primeiro', 'segundo']:
        eventos_tempo = sorted([e for e in events if e['tempo'] == tempo], 
                             key=lambda x: x['segundos'])
        
        for i in range(len(eventos_tempo)-1):
            if eventos_tempo[i]['parado']:
                diff = eventos_tempo[i+1]['segundos'] - eventos_tempo[i]['segundos']
                resultados[tempo] += diff
    
    # Exibição dos resultados
    st.subheader('Resultados:')
    
    for tempo in ['primeiro', 'segundo']:
        total = resultados[tempo]
        minutos = total // 60
        segundos = total % 60
        
        st.metric(
            label=f'Tempo {tempo} parado',
            value=f'{minutos:02d}:{segundos:02d}',
            help='Tempo acumulado devido a substituições, faltas, laterais, etc.'
        )
