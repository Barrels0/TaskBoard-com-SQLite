#streamlit run trello.py
import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="TaskBoard", layout="centered")

conexao = sqlite3.connect("tarefas.db",check_same_thread=False)
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        status TEXT NOT NULL
    )
''')
conexao.commit()

st.title("📌 Meu TaskBoard")
st.write("Gerencie suas tarefas e acompanhe seu progresso.")

st.divider()

st.subheader("➕ Nova Tarefa")

col1,col2 = st.columns([3,1])

with col1:
    nova_tarefa = st.text_input("Nome da tarefa", label_visibility="collapsed",placeholder="O que precisa ser feito?")
with col2:
    if st.button("Adicionar", use_container_width=True):
        if nova_tarefa:
            cursor.execute("INSERT INTO tarefas (nome, status) VALUES (?, ?)",(nova_tarefa,"Pendente"))
            conexao.commit()
            st.rerun() #salva no banco e recarrega a pagina para que a tarefa apareça
        else:
            st.warning("Digite o nome de uma tarefa!")

st.divider()

st.subheader("📋 Suas Tarefas")

df_tarefa = pd.read_sql_query("SELECT id, nome, status FROM tarefas WHERE status = 'Pendente'",conexao) #lê oq eu peço na query e cria uma tabela
if df_tarefa.empty:
    st.info("Nenhuma tarefa cadastrada ainda. Adicione uma acima!")
else: 
    st.dataframe(df_tarefa, hide_index=True, use_container_width=True)
st.divider()

with st.expander("✅ Tarefas concluidas"):
    st.subheader("✅ Tarefas concluidas")
    df_tarefa = pd.read_sql_query("SELECT id, nome, status FROM tarefas WHERE status = 'Concluido'",conexao) #lê oq eu peço na query e cria uma tabela
    if df_tarefa.empty:
        st.info("Nenhuma tarefa cadastrada foi concluida até o momento!")
    else: 
        st.dataframe(df_tarefa, hide_index=True, use_container_width=True)

st.divider()

col_update, col_delete = st.columns(2)

with col_update:
    st.subheader("🔄 Atualizar Status")
    tarefas_pendentes = pd.read_sql_query("SELECT id, nome FROM tarefas WHERE status = 'Pendente'",conexao)

    if not tarefas_pendentes.empty:
        tarefa_select = st.selectbox("Seleciona para concluir:",tarefas_pendentes['nome'])

        if st.button("✅ Marcar como Concluída", use_container_width=True):
            id_tarefa = tarefas_pendentes.loc[tarefas_pendentes['nome'] == tarefa_select, 'id'].values[0]

            cursor.execute("UPDATE tarefas SET status = 'Concluido' WHERE id = ?",(int(id_tarefa),))
            conexao.commit()
            st.rerun()
    else:
        st.success("Tudo limpo! Nenhuma tarefa pendente.")
with col_delete: 
    st.subheader("🗑️ Excluir Tarefa")
    if not tarefas_pendentes.empty:
        tarefa_excluir = st.selectbox("Selecione para excluir:",df_tarefa['nome'])
        if st.button("❌ Excluir Definitivamente", use_container_width=True):
            id_excluir = df_tarefa.loc[df_tarefa['nome'] == tarefa_excluir, "id"].values[0]

            cursor.execute("DELETE FROM tarefas WHERE id = ?",(int(id_excluir),))
            conexao.commit()
            st.rerun()
        else:
            st.info("Nenhuma tarefa para excluir.")