import streamlit as st
import re
import pandas as pd
from datetime import timedelta

def converter_timestamp_para_segundos(timestamp):
    # Implementação conforme código anterior
    pass

def é_evento_de_paralisação(evento):
    # Implementação conforme código anterior
    pass

def processar_paralisações(eventos):
    # Processa eventos para calcular tempo de paralisação
    em_paralisação = False
    tempo_inicio_paralisação = 0
    tempo_total_paralisação = 0
    
    for i, evento in enumerate(eventos):
        partes = evento.split("''", 1)
        if len(partes) < 2:
            continue
            
        timestamp = partes[0] + "''"
        descrição = partes[1].strip()
        
        tempo_atual = converter_timestamp_para_segundos(timestamp)
        
        if é_evento_de_paralisação(descrição):
            if not em_paralisação:
                em_paralisação = True
                tempo_inicio_paralisação = tempo_atual
        else:
            if em_paralisação:
                em_paralisação = False
                tempo_paralisação = tempo_atual - tempo_inicio_paralisação
                tempo_total_paralisação += tempo_paralisação
    
    return tempo_total_paralisação

def main():
    st.title("Calculadora de Tempo de Paralisação em Jogos de Futebol")
    
    idioma = st.radio("Selecione o idioma dos eventos:", ["Português", "Inglês"])
    
    eventos_texto = st.text_area("Cole aqui os eventos da partida:", height=400)
    
    if st.button("Calcular Tempo de Paralisação"):
        if eventos_texto:
            eventos = eventos_texto.strip().split("\n")
            
            tempo_paralisação_1t, tempo_paralisação_2t = calcular_tempo_paralisação(eventos)
            
            st.success("Cálculo concluído!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Tempo de Paralisação - 1º Tempo", 
                         str(timedelta(seconds=tempo_paralisação_1t)))
            
            with col2:
                st.metric("Tempo de Paralisação - 2º Tempo", 
                         str(timedelta(seconds=tempo_paralisação_2t)))
            
            st.metric("Tempo Total de Paralisação", 
                     str(timedelta(seconds=tempo_paralisação_1t + tempo_paralisação_2t)))
        else:
            st.error("Por favor, insira os eventos da partida.")

def é_evento_de_paralisação(evento, idioma="Inglês"):
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
def mostrar_resultados_gráficos(tempo_1t, tempo_2t):
    tempos = [tempo_1t, tempo_2t]
    labels = ["1º Tempo", "2º Tempo"]
    
    fig, ax = plt.subplots()
    ax.bar(labels, tempos)
    ax.set_ylabel("Tempo (segundos)")
    ax.set_title("Tempo de Paralisação por Período")
    
    st.pyplot(fig)


if __name__ == "__main__":
    main()
