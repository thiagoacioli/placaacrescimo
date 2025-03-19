import streamlit as st
import re
from datetime import datetime, timedelta

def extrair_eventos(texto_eventos):
    """
    Extrai eventos do texto inserido no formato específico do radar.
    Suporta formatos como "52'32''Clearance by Netherlands U19" ou "45' + 0'55''Dangerous Attack by Netherlands U19"
    """
    eventos = []
    linhas = texto_eventos.strip().split('\n')
    
    # Padrão para capturar o tempo em formatos como "52'32''" ou "45' + 0'55''"
    padrao_tempo = re.compile(r'(\d+)\'(?:\s*\+\s*)?(\d+)?\'?(?:(\d+)\'\')?(.+)')
    
    for linha in linhas:
        if not linha.strip() or linha.strip() == "Half Time" or linha.strip() == "1st Half Kick-off":
            # Evento especial para marcar o intervalo
            if linha.strip() == "Half Time":
                eventos.append(("Half Time", None, None, "Half Time"))
            continue
            
        match = padrao_tempo.match(linha)
        if match:
            minuto_base = int(match.group(1))
            acrescimo = int(match.group(2)) if match.group(2) else 0
            segundo = int(match.group(3)) if match.group(3) else 0
            descricao = match.group(4).strip()
            
            # Calcular o tempo total em segundos para facilitar a ordenação
            tempo_total = (minuto_base + acrescimo) * 60 + segundo
            
            eventos.append((minuto_base, acrescimo, segundo, descricao, tempo_total))
    
    # Ordenar eventos por tempo
    eventos.sort(key=lambda x: x[4] if isinstance(x[4], int) else 0)
    
    return eventos

def identificar_paralisacoes(eventos):
    """
    Identifica eventos de paralisação com base em palavras-chave.
    """
    # Palavras-chave que indicam paralisação
    palavras_paralisacao = [
        'Free Kick', 'Corner', 'Goal Kick', 'Throw In', 'Substitution', 
        'Yellow Card', 'Red Card', 'Goal', 'Kick-off', 'Shot On Target',
        'Shot Off Target', 'VAR', 'Treatment', 'Injury', 'Offside'
    ]
    
    # Eventos que normalmente não causam paralisação
    eventos_sem_paralisacao = [
        'Attack', 'Dangerous Attack', 'Clearance', 'Blocked Shot'
    ]
    
    paralisacoes = []
    inicio_paralisacao = None
    
    for i, evento in enumerate(eventos):
        if isinstance(evento[0], str) and evento[0] == "Half Time":
            continue
            
        minuto_base, acrescimo, segundo, descricao, tempo_total = evento
        
        # Verifica se é um evento de paralisação
        e_paralisacao = any(palavra in descricao for palavra in palavras_paralisacao)
        e_continuacao = any(palavra in descricao for palavra in eventos_sem_paralisacao)
        
        if e_paralisacao and not inicio_paralisacao:
            inicio_paralisacao = evento
        elif e_continuacao and inicio_paralisacao:
            # Calcular duração da paralisação
            duracao = tempo_total - inicio_paralisacao[4]
            
            # Converter duração para minutos e segundos
            duracao_minutos = duracao // 60
            duracao_segundos = duracao % 60
            
            # Só registrar paralisações que duraram pelo menos 5 segundos
            if duracao >= 5:
                paralisacoes.append((
                    inicio_paralisacao,
                    evento,
                    duracao_minutos,
                    duracao_segundos
                ))
            
            inicio_paralisacao = None
    
    return paralisacoes

def calcular_tempo_paralisacao(paralisacoes):
    """
    Calcula o tempo total de paralisação no primeiro e segundo tempo.
    """
    primeiro_tempo = []
    segundo_tempo = []
    
    for paralisacao in paralisacoes:
        inicio, fim, duracao_minutos, duracao_segundos = paralisacao
        
        # Verificar se a paralisação ocorreu no primeiro ou segundo tempo
        if inicio[0] < 45 or (inicio[0] == 45 and inicio[1] > 0):
            primeiro_tempo.append((duracao_minutos, duracao_segundos))
        else:
            segundo_tempo.append((duracao_minutos, duracao_segundos))
    
    # Calcular o tempo total de paralisação em segundos
    tempo_primeiro = sum(m * 60 + s for m, s in primeiro_tempo)
    tempo_segundo = sum(m * 60 + s for m, s in segundo_tempo)
    
    return tempo_primeiro, tempo_segundo, primeiro_tempo, segundo_tempo

def formatar_tempo(segundos):
    """Formata o tempo em segundos para minutos e segundos."""
    minutos = segundos // 60
    segundos_restantes = segundos % 60
    return f"{minutos} min e {segundos_restantes} seg"

def formatar_evento(evento):
    """Formata um evento para exibição."""
    if isinstance(evento[0], str) and evento[0] == "Half Time":
        return "Half Time"
        
    minuto_base, acrescimo, segundo, descricao, _ = evento
    if acrescimo > 0:
        return f"{minuto_base}' + {acrescimo}'{segundo}'' {descricao}"
    else:
        return f"{minuto_base}'{segundo}'' {descricao}"

def main():
    st.title("Calculadora de Tempo de Paralisação em Partidas")
    
    st.markdown("""
    ## Instruções
    1. Cole os eventos da partida no formato do radar no campo abaixo
    2. O aplicativo reconhece formatos como:
       - `52'32''Clearance by Netherlands U19`
       - `45' + 0'55''Dangerous Attack by Netherlands U19`
    3. O aplicativo identificará automaticamente os eventos de paralisação
    """)
    
    # Campo para inserção dos eventos
    texto_eventos = st.text_area("Cole os eventos da partida abaixo:", height=300)
    
    if st.button("Calcular Tempo de Paralisação"):
        if texto_eventos:
            eventos = extrair_eventos(texto_eventos)
            
            if eventos:
                # Identificar paralisações
                paralisacoes = identificar_paralisacoes(eventos)
                
                # Calcular tempo de paralisação
                tempo_primeiro, tempo_segundo, paralisacoes_primeiro, paralisacoes_segundo = calcular_tempo_paralisacao(paralisacoes)
                
                # Exibir resultados
                st.subheader("Resumo das Paralisações")
                
                # Primeiro tempo
                st.markdown("### Primeiro Tempo")
                if paralisacoes_primeiro:
                    for i, (minutos, segundos) in enumerate(paralisacoes_primeiro, 1):
                        st.write(f"Paralisação {i}: {minutos} min e {segundos} seg")
                    st.success(f"Tempo total de paralisação no primeiro tempo: {formatar_tempo(tempo_primeiro)}")
                else:
                    st.info("Nenhuma paralisação identificada no primeiro tempo.")
                
                # Segundo tempo
                st.markdown("### Segundo Tempo")
                if paralisacoes_segundo:
                    for i, (minutos, segundos) in enumerate(paralisacoes_segundo, 1):
                        st.write(f"Paralisação {i}: {minutos} min e {segundos} seg")
                    st.success(f"Tempo total de paralisação no segundo tempo: {formatar_tempo(tempo_segundo)}")
                else:
                    st.info("Nenhuma paralisação identificada no segundo tempo.")
                
                # Total geral
                tempo_total = tempo_primeiro + tempo_segundo
                st.subheader(f"Tempo total de paralisação na partida: {formatar_tempo(tempo_total)}")
                
                # Opção para ver detalhes das paralisações
                if st.checkbox("Ver detalhes das paralisações"):
                    st.subheader("Detalhes das Paralisações")
                    for i, (inicio, fim, duracao_minutos, duracao_segundos) in enumerate(paralisacoes, 1):
                        st.write(f"Paralisação {i}: {duracao_minutos} min e {duracao_segundos} seg")
                        st.write(f"- Início: {formatar_evento(inicio)}")
                        st.write(f"- Fim: {formatar_evento(fim)}")
                        st.write("---")
                
                # Opção para ver todos os eventos
                if st.checkbox("Ver todos os eventos"):
                    st.subheader("Todos os Eventos")
                    for evento in eventos:
                        if isinstance(evento[0], str) and evento[0] == "Half Time":
                            st.write("Half Time")
                        else:
                            st.write(formatar_evento(evento))
            else:
                st.error("Não foi possível identificar eventos no formato correto. Por favor, verifique o formato dos eventos inseridos.")
        else:
            st.warning("Por favor, insira os eventos da partida para calcular o tempo de paralisação.")

if __name__ == "__main__":
    main()
