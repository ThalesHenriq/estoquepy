import streamlit as st
import json
import os
from datetime import datetime

# Arquivo para persistência do estoque
ESTOQUE_FILE = 'estoque_data.json'

# Carregar dados existentes
def load_estoque():
    if os.path.exists(ESTOQUE_FILE):
        with open(ESTOQUE_FILE, 'r') as f:
            return json.load(f)
    return {}  # {produto: {'quantidade': int, 'preco': float}}

# Salvar dados
def save_estoque(estoque):
    with open(ESTOQUE_FILE, 'w') as f:
        json.dump(estoque, f)

# Interface
st.title("Gestor de Estoque para Vendas - Ajuda ao RH e Vendas")

estoque = load_estoque()

# Tabs
tab1, tab2, tab3 = st.tabs(["Gerenciar Estoque", "Registrar Venda", "Relatório de Estoque"])

with tab1:
    st.header("Adicionar ou Atualizar Produto")
    nome_prod = st.text_input("Nome do Produto", value="")
    quantidade = st.number_input("Quantidade", min_value=0, value=0)
    preco = st.number_input("Preço Unitário (R$)", min_value=0.0, value=0.0, step=0.01)

    if st.button("Adicionar/Atualizar Produto"):
        if nome_prod.strip():
            if nome_prod in estoque:
                estoque[nome_prod]['quantidade'] += quantidade
                estoque[nome_prod]['preco'] = preco  # Atualiza preço se alterado
                st.success(f"Produto '{nome_prod}' atualizado: {estoque[nome_prod]['quantidade']} unidades a R$ {preco:.2f} cada.")
            else:
                estoque[nome_prod] = {'quantidade': quantidade, 'preco': preco}
                st.success(f"Produto '{nome_prod}' adicionado: {quantidade} unidades a R$ {preco:.2f} cada.")
            save_estoque(estoque)
        else:
            st.warning("Digite o nome do produto.")

    st.subheader("Remover Produto")
    prod_remover = st.selectbox("Selecione Produto para Remover", options=list(estoque.keys()) or ["Nenhum"])
    if prod_remover != "Nenhum" and st.button("Remover"):
        del estoque[prod_remover]
        save_estoque(estoque)
        st.success(f"Produto '{prod_remover}' removido.")
        st.rerun()

with tab2:
    st.header("Registrar Venda")
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []

    st.subheader("Adicionar ao Carrinho")
    prod_venda = st.selectbox("Selecione Produto", options=list(estoque.keys()) or ["Nenhum"])
    qtd_venda = st.number_input("Quantidade a Vender", min_value=1, value=1)

    if prod_venda != "Nenhum" and st.button("Adicionar ao Carrinho"):
        if estoque[prod_venda]['quantidade'] >= qtd_venda:
            st.session_state.carrinho.append({'produto': prod_venda, 'qtd': qtd_venda, 'preco': estoque[prod_venda]['preco']})
            st.success(f"{qtd_venda} unidades de '{prod_venda}' adicionadas ao carrinho.")
        else:
            st.warning(f"Estoque insuficiente para '{prod_venda}'. Disponível: {estoque[prod_venda]['quantidade']}.")

    # Exibir carrinho
    if st.session_state.carrinho:
        st.subheader("Carrinho Atual")
        total_venda = 0
        for i, item in enumerate(st.session_state.carrinho):
            col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
            col1.write(item['produto'])
            col2.write(f"Qtd: {item['qtd']}")
            subtotal = item['qtd'] * item['preco']
            col3.write(f"Subtotal: R$ {subtotal:.2f}")
            if col4.button("Remover", key=f"rem_carr_{i}"):
                del st.session_state.carrinho[i]
                st.rerun()
            total_venda += subtotal

        st.markdown(f"**Total da Venda:** R$ {total_venda:.2f}")

        if st.button("Finalizar Venda"):
            for item in st.session_state.carrinho:
                estoque[item['produto']]['quantidade'] -= item['qtd']
            save_estoque(estoque)
            st.session_state.carrinho = []
            st.success(f"Venda finalizada! Total: R$ {total_venda:.2f}. Estoque atualizado.")
            st.rerun()

with tab3:
    st.header("Relatório de Estoque")
    if estoque:
        for prod, info in sorted(estoque.items()):
            st.write(f"- {prod.capitalize()}: {info['quantidade']} unidades a R$ {info['preco']:.2f} cada (Valor total: R$ {info['quantidade'] * info['preco']:.2f})")
        total_itens = sum(info['quantidade'] for info in estoque.values())
        total_valor = sum(info['quantidade'] * info['preco'] for info in estoque.values())
        st.write(f"**Total de Itens:** {total_itens}")
        st.write(f"**Valor Total em Estoque:** R$ {total_valor:.2f}")
    else:
        st.info("Estoque vazio.")
