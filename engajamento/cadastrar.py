import streamlit as st
import pandas as pd
from db_connection import get_db_connection
import sqlite3

st.markdown("<h3>Registro de Engajamentos</h3>", unsafe_allow_html=True)

# --- Funções para gerenciar o banco de dados SQLite ---
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # SQLite-specific query should be changed to work with both databases
    # For PostgreSQL compatibility:
    c.execute('''
        CREATE TABLE IF NOT EXISTS engajamentos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            engajamento_id TEXT NOT NULL,
            tipo TEXT NOT NULL,
            funcionando TEXT NOT NULL DEFAULT 'Sim'
        )
    ''')
    conn.commit()
    conn.close()

def add_missing_columns():
    conn = get_db_connection()
    c = conn.cursor()
    
    # This needs to be handled differently for PostgreSQL vs SQLite
    import os
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # PostgreSQL approach
        c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='engajamentos'")
        columns = [col[0] for col in c.fetchall()]
        
        if "funcionando" not in columns:
            c.execute("ALTER TABLE engajamentos ADD COLUMN funcionando TEXT NOT NULL DEFAULT 'Sim'")
        if "tipo" not in columns:
            c.execute("ALTER TABLE engajamentos ADD COLUMN tipo TEXT NOT NULL DEFAULT 'Like'")
    else:
        # SQLite approach (original code)
        c.execute("PRAGMA table_info(engajamentos)")
        columns = [col[1] for col in c.fetchall()]
        if "funcionando" not in columns:
            c.execute("ALTER TABLE engajamentos ADD COLUMN funcionando TEXT NOT NULL DEFAULT 'Sim'")
        if "tipo" not in columns:
            c.execute("ALTER TABLE engajamentos ADD COLUMN tipo TEXT NOT NULL DEFAULT 'Like'")
    
    conn.commit()
    conn.close()

def insert_engajamento(nome, engajamento_id, tipo):
    conn = get_db_connection()
    c = conn.cursor()
    
    import os
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # PostgreSQL uses %s for parameters
        c.execute("INSERT INTO engajamentos (nome, engajamento_id, tipo, funcionando) VALUES (%s, %s, %s, %s)", 
                  (nome, engajamento_id, tipo, "Sim"))
    else:
        # SQLite uses ? for parameters
        c.execute("INSERT INTO engajamentos (nome, engajamento_id, tipo, funcionando) VALUES (?, ?, ?, ?)", 
                  (nome, engajamento_id, tipo, "Sim"))
    
    conn.commit()
    conn.close()

def get_engajamentos():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, nome, engajamento_id, tipo, funcionando FROM engajamentos")
    rows = c.fetchall()
    conn.close()
    return rows

def update_engajamento(row_id, nome, engajamento_id, tipo, funcionando):
    conn = get_db_connection()
    c = conn.cursor()
    
    import os
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # PostgreSQL uses %s
        c.execute("UPDATE engajamentos SET nome=%s, engajamento_id=%s, tipo=%s, funcionando=%s WHERE id=%s", 
                  (nome, engajamento_id, tipo, funcionando, row_id))
    else:
        # SQLite uses ?
        c.execute("UPDATE engajamentos SET nome=?, engajamento_id=?, tipo=?, funcionando=? WHERE id=?", 
                  (nome, engajamento_id, tipo, funcionando, row_id))
    
    conn.commit()
    conn.close()

def delete_engajamento(row_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    import os
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # PostgreSQL
        c.execute("DELETE FROM engajamentos WHERE id=%s", (row_id,))
    else:
        # SQLite
        c.execute("DELETE FROM engajamentos WHERE id=?", (row_id,))
    
    conn.commit()
    conn.close()

# Inicializa o banco de dados e garante que as colunas existam
init_db()
add_missing_columns()

# --- Formulário de cadastro em expansão ---
with st.expander("Cadastrar Novo Engajamento", expanded=False):
    with st.form("cadastro_engajamento"):
        engajamento_nome = st.text_input("Nome do Engajamento", placeholder="Digite o nome do engajamento")
        engajamento_id = st.text_input("ID do Engajamento", placeholder="Digite o ID do engajamento")
        engajamento_tipo = st.selectbox("Tipo de Engajamento", options=["Like", "Amei", "Uau"])
        
        submitted = st.form_submit_button("Salvar Engajamento")
        if submitted:
            if engajamento_nome and engajamento_id:
                insert_engajamento(engajamento_nome, engajamento_id, engajamento_tipo)
                st.success("Engajamento salvo com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos.")

# --- Exibe os engajamentos cadastrados em uma tabela simples ---
st.markdown("### Engajamentos Cadastrados")
rows = get_engajamentos()

if rows:
    # Cria DataFrame para exibição
    df = pd.DataFrame(rows, columns=["ID", "Nome", "ID do Engajamento", "Tipo", "Funcionando?"])
    
    # Exibe a tabela simples
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    # --- Seção para excluir engajamentos ---
    st.markdown("### Excluir Engajamentos")
    
    # Seleciona engajamentos para excluir
    delete_options = [f"{row[0]} - {row[1]}" for row in rows]
    selected_delete_options = st.multiselect("Selecione engajamentos para excluir:", delete_options)
    
    if selected_delete_options:
        # Extrai IDs das seleções
        delete_ids = [int(option.split(" - ")[0]) for option in selected_delete_options]
        
        # Botão para confirmar exclusão
        if st.button("Excluir Selecionados"):
            for id_to_delete in delete_ids:
                delete_engajamento(id_to_delete)
            st.success(f"{len(delete_ids)} engajamento(s) excluído(s) com sucesso!")
            st.rerun()
else:
    st.info("Nenhum engajamento cadastrado ainda.")