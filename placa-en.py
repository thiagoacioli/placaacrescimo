import streamlit as st
import re
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

def converter_timestamp_para_segundos(timestamp):
    """Converte um timestamp no formato de futebol para segundos totais."""
    # Para timestamps como "90' + 3'31''"
    if '+' in timestamp:
        match = re.match(r"(\d+)'\s*\+\s*(\d+)'(\d+)''", timestamp)
        if match:
            minutos_normais = int(match.group(1))
            minutos_acrescimo = int(match.group(2))
            segundos = int(match.group(3))
            return (minutos_normais * 60) + (minutos_acrescimo * 60) + segundos
    
    # Para timestamps como "89'58''"
    else:
        match = re.match(r"(\d+)'(\d+)''", timestamp)
        if match:
            minutos = int(match.group(1))
            segundos = int(match.group(2))
            return (minutos * 60) + segundos
    
    return 0  # Caso não consiga fazer o parse

def é_evento_de_paralisação(evento, idioma="Inglês"):
    """Verifica se um evento é considerado uma paralisação."""
    eventos_paralisação = {
        "Inglês": [
            "Substitution", "Yellow Card", "Red Card", 
            "Free Kick", "Goal Kick", "Corner",
            "Throw In", "Kick-off"
        ],
        "Português": [
            "Substituição", "Cartão Amarelo", "Cartão Vermelho",
            "Tiro Livre", "Tiro de Meta", "Escanteio",
            "Lateral", "Início de Jogo"
        ]
    }
    
    lista_eventos = eventos_paralisação.get(idioma, eventos_paralisação["Inglês"])
    
    for tipo in lista_eventos:
        if tipo in evento:
            return True
    return False

def extrair_timestamp_e_descrição(evento):
    """Extrai o timestamp e a descrição de um evento."""
    # Tenta separar pelo padrão ''
    partes = evento.split("''", 1)
    if len(partes) == 2:
        timestamp = partes[0] + "''"
        descrição = partes[1].strip()
        return timestamp, descrição
    
    # Se não conseguir separar, tenta outros padrões
    match = re.match(r"([\d\s'\+]+)(.*)", evento)
    if match:
        timestamp = match.group(1).strip()
        descrição = match.group(2).strip()
        # Adiciona '' se necessário
        if not timestamp.endswith("''"):
            timestamp += "''"
        return timestamp, descrição
    
    return "", evento  # Retorna vazio para timestamp se não conseguir extrair

def processar_paralisações(eventos, idioma="Inglês"):
    """Processa uma lista de eventos para calcular o tempo total de paralisação."""
    eventos_processados = []
    tempo_total_paralisação = 0
    
    # Pré-processar eventos para extrair timestamp e descrição
    for evento in eventos:
        if evento.strip():  # Ignora linhas vazias
            timestamp, descrição = extrair_timestamp_e_descrição(evento)
            tempo_segundos = converter_timestamp_para_segundos(timestamp)
            eventos_processados.append((tempo_segundos, descrição))
    
    # Ordenar eventos por tempo
    eventos_processados.sort(key=lambda x: x[0])
    
    # Identificar sequências de paralisação
    i = 0
    while i < len(eventos_processados) - 1:
        tempo_atual, descrição_atual = eventos_processados[i]
        
        if é_evento_de_paralisação(descrição_atual, idioma):
            # Encontrou início de paralisação
            tempo_inicio = tempo_atual
            
            # Procura o próximo evento que não é paralisação
            j = i + 1
            while j < len(eventos_processados):
                tempo_próximo, descrição_próxima = eventos_processados[j]
                
                if not é_evento_de_paralisação(descrição_próxima, idioma):
                    # Encontrou o fim da paralisação
                    tempo_fim = tempo_próximo
                    tempo_paralisação = tempo_fim - tempo_inicio
                    tempo_total_paralisação += tempo_paralisação
                    i = j  # Pula para o próximo evento após a paralisação
                    break
                j += 1
                
            if j >= len(eventos_processados):
                # Se chegou ao fim da lista, encerra o loop
                break
        i += 1
    
    return tempo_total_paralisação

def calcular_tempo_paralisação(eventos, idioma="Inglês"):
    """Separa os eventos em primeiro e segundo tempo e calcula as paralisações."""
    primeiro_tempo = []
    segundo_tempo = []
    
    # Separar eventos em primeiro e segundo tempo
    em_primeiro_tempo = True
    
    for evento in eventos:
        if "Half Time" in evento or "Intervalo" in evento:
            em_primeiro_tempo = False
            continue
        
        if "Full Time" in evento or "Fim de Jogo" in evento:
            continue
        
        if em_primeiro_tempo:
            primeiro_tempo.append(evento)
        else:
            segundo_tempo.append(evento)
    
    # Calcular paralisações em cada tempo
    tempo_paralisação_1t = processar_paralisações(primeiro_tempo, idioma)
    tempo_paralisação_2t = processar_paralisações(segundo_tempo, idioma)
    
    return tempo_paralisação_1t, tempo_paralisação_2t

def formatar_tempo(segundos):
    """Formata um tempo em segundos para o formato minutos:segundos."""
    minutos = int(segundos / 60)
    segundos_restantes = int(segundos % 60)
    return f"{minutos}:{segundos_restantes:02d}"

def mostrar_resultados_gráficos(tempo_1t, tempo_2t):
    """Gera um gráfico de barras mostrando o tempo de paralisação por período."""
    tempos = [tempo_1t, tempo_2t, tempo_1t + tempo_2t]
    labels = ["1º Tempo", "2º Tempo", "Total"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    barras = ax.bar(labels, tempos, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    
    # Adicionar rótulos nas barras
    for barra in barras:
        altura = barra.get_height()
        minutos = int(altura / 60)
        segundos = int(altura % 60)
        ax.text(barra.get_x() + barra.get_width()/2., altura + 30,
                f'{minutos}:{segundos:02d}',
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel("Tempo (segundos)")
    ax.set_title("Tempo de Paralisação por Período")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    st.pyplot(fig)

def main():
    st.set_page_config(
        page_title="Calculadora de Tempo de Paralisação",
        page_icon="⚽",
        layout="wide"
    )
    
    st.title("⚽ Calculadora de Tempo de Paralisação em Jogos de Futebol")
    st.markdown("Calcule quanto tempo o jogo ficou parado durante a partida")
    
    idioma = st.radio("Selecione o idioma dos eventos:", ["Português", "Inglês"])
    
    # Exemplo para ajudar o usuário
    exemplo = """45' + 0'55''Dangerous Attack by Netherlands U19
45' + 0'53''Attack by Netherlands U19
Half Time
45'00''Kick-off for Croatia U19"""
    
    eventos_texto = st.text_area(
        "Cole aqui os eventos da partida:", 
        height=400,
        placeholder=exemplo
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Calcular", use_container_width=True):
            if eventos_texto:
                eventos = eventos_texto.strip().split("\n")
                
                with st.spinner("Calculando tempos de paralisação..."):
                    tempo_paralisação_1t, tempo_paralisação_2t = calcular_tempo_paralisação(eventos, idioma)
                
                st.success("Cálculo concluído!")
                
                # Armazenar resultados na sessão para uso posterior
                st.session_state.tempo_1t = tempo_paralisação_1t
                st.session_state.tempo_2t = tempo_paralisação_2t
                st.session_state.calculado = True
            else:
                st.error("Por favor, insira os eventos da partida.")
    
    with col2:
        st.empty()
    
    if 'calculado' in st.session_state and st.session_state.calculado:
        tempo_1t = st.session_state.tempo_1t
        tempo_2t = st.session_state.tempo_2t
        
        st.subheader("Resultados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "1º Tempo", 
                formatar_tempo(tempo_1t),
                delta=f"{int(tempo_1t / 60)} minutos"
            )
        
        with col2:
            st.metric(
                "2º Tempo", 
                formatar_tempo(tempo_2t),
                delta=f"{int(tempo_2t / 60)} minutos"
            )
        
        with col3:
            st.metric(
                "Tempo Total", 
                formatar_tempo(tempo_1t + tempo_2t),
                delta=f"{int((tempo_1t + tempo_2t) / 60)} minutos"
            )
        
        # Mostrar gráfico
        mostrar_resultados_gráficos(tempo_1t, tempo_2t)
        
        # Opção para download dos resultados
        dados = {
            "Período": ["1º Tempo", "2º Tempo", "Total"],
            "Tempo (s)": [tempo_1t, tempo_2t, tempo_1t + tempo_2t],
            "Tempo (min:seg)": [
                formatar_tempo(tempo_1t),
                formatar_tempo(tempo_2t),
                formatar_tempo(tempo_1t + tempo_2t)
            ],
            "Minutos": [
                round(tempo_1t / 60, 2),
                round(tempo_2t / 60, 2),
                round((tempo_1t + tempo_2t) / 60, 2)
            ]
        }
        
        df = pd.DataFrame(dados)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="Baixar resultados como CSV",
            data=csv,
            file_name="tempo_paralisacao.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
