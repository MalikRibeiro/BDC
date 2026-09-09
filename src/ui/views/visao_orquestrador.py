import streamlit as st
import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(".")

def obter_ultimo_log_runner() -> tuple[Path | None, str]:
    logs_dir = BASE_DIR / "LOGS" / "runner"
    if not logs_dir.exists():
        logs_dir = BASE_DIR / "LOGS" / "execucao"
        
    if not logs_dir.exists():
        return None, "Pasta de logs não encontrada."
        
    arquivos_log = list(logs_dir.glob("*.log"))
    if not arquivos_log:
        return None, "Nenhum arquivo de log encontrado."
        
    arquivos_log.sort(key=os.path.getmtime, reverse=True)
    ultimo_log = arquivos_log[0]
    
    try:
        with open(ultimo_log, "r", encoding="utf-8", errors="replace") as f:
            linhas = f.readlines()
            ultimas_linhas = linhas[-80:] if len(linhas) > 80 else linhas
            return ultimo_log, "".join(ultimas_linhas)
    except Exception as e:
        return ultimo_log, f"Erro ao ler log: {e}"

def render_visao_orquestrador():
    st.header("Pipeline BDC")
    
    # Inicializa estado do processo e arquivo de saída
    if "pipeline_proc" not in st.session_state:
        st.session_state.pipeline_proc = None
        st.session_state.pipeline_inicio = None
        st.session_state.pipeline_log_file = None
        
    proc = st.session_state.pipeline_proc
    esta_executando = False
    
    if proc is not None:
        codigo_retorno = proc.poll()
        if codigo_retorno is None:
            esta_executando = True
        else:
            if codigo_retorno == 0:
                st.success("Última execução do pipeline foi concluída com sucesso!")
            else:
                st.error(f"O pipeline terminou com código de erro: {codigo_retorno}")
            st.session_state.pipeline_proc = None

    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if esta_executando:
            tempo_decorrido = int((datetime.now() - st.session_state.pipeline_inicio).total_seconds()) if st.session_state.pipeline_inicio else 0
            st.warning(f"Pipeline em execução... ({tempo_decorrido}s decorridos)")
            if st.button("Interromper Execução (Kill)", type="secondary"):
                proc.terminate()
                st.session_state.pipeline_proc = None
                st.warning("Processo interrompido.")
                st.rerun()
        else:
            if st.button("Executar", type="primary", use_container_width=True):
                try:
                    runner_logs_dir = BASE_DIR / "LOGS" / "runner"
                    runner_logs_dir.mkdir(parents=True, exist_ok=True)
                    log_stdout_path = runner_logs_dir / f"STDOUT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    
                    # Abre arquivo de saída para redirecionar stdout/stderr sem risco de deadlock de buffer
                    log_file_handle = open(log_stdout_path, "w", encoding="utf-8")
                    
                    novo_proc = subprocess.Popen(
                        [sys.executable, "main.py"],
                        cwd=str(BASE_DIR.resolve()),
                        stdout=log_file_handle,
                        stderr=subprocess.STDOUT
                    )
                    st.session_state.pipeline_proc = novo_proc
                    st.session_state.pipeline_inicio = datetime.now()
                    st.session_state.pipeline_log_file = str(log_stdout_path)
                    st.success("Pipeline iniciado em segundo plano!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Falha ao iniciar processo: {e}")

    with col3:
        if st.button("Atualizar Log", use_container_width=True):
            st.rerun()
            
    st.markdown("---")
    
    # Monitor de Logs em Tempo Real
    st.subheader("Log de Execução do Pipeline")
    caminho_log, conteudo_log = obter_ultimo_log_runner()
    
    if caminho_log:
        st.caption(f"Visualizando arquivo: `{caminho_log}` (últimas 80 linhas)")
        st.code(conteudo_log, language="log")
    else:
        st.info(conteudo_log)

    # Se o pipeline estiver rodando, faz polling/refresh a cada 2 segundos
    if esta_executando:
        time.sleep(2)
        st.rerun()
