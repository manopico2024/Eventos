import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
import sqlite3
from fpdf import FPDF

# Conexão com o banco de dados SQLite
conn = sqlite3.connect("roadmap.db")
cursor = conn.cursor()

# Criar tabela no banco de dados
cursor.execute("""
CREATE TABLE IF NOT EXISTS roadmap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarefa TEXT NOT NULL,
    status TEXT NOT NULL,
    descricao TEXT
)
""")
conn.commit()

# Função para carregar dados do banco de dados
def carregar_dados():
    cursor.execute("SELECT tarefa, status, descricao FROM roadmap")
    return [{"Tarefa": row[0], "Status": row[1], "Descrição": row[2]} for row in cursor.fetchall()]

# Carregar dados iniciais
roadmap = carregar_dados()

# Função para atualizar a tabela
def atualizar_tabela(filtrado=None):
    for row in tree.get_children():
        tree.delete(row)
    dados = filtrado if filtrado else roadmap
    for item in dados:
        tree.insert("", "end", values=(item["Tarefa"], item["Status"], item["Descrição"][:50] + ("..." if len(item["Descrição"]) > 50 else "")))

# Função para pesquisar itens
def pesquisar():
    termo = entry_pesquisa.get().lower()
    filtrado = [item for item in roadmap if termo in item["Tarefa"].lower() or termo in item["Descrição"].lower()]
    atualizar_tabela(filtrado)

# Função para adicionar uma nova tarefa
def adicionar_tarefa():
    nova_tarefa = entry_tarefa.get().strip()
    nova_descricao = text_descricao.get("1.0", tk.END).strip()
    if nova_tarefa and nova_descricao:
        roadmap.append({"Tarefa": nova_tarefa, "Status": "Pendente", "Descrição": nova_descricao})
        cursor.execute("INSERT INTO roadmap (tarefa, status, descricao) VALUES (?, ?, ?)",
                       (nova_tarefa, "Pendente", nova_descricao))
        conn.commit()
        entry_tarefa.delete(0, tk.END)
        text_descricao.delete("1.0", tk.END)
        atualizar_tabela()
        messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")
    else:
        messagebox.showwarning("Entrada inválida", "Por favor, preencha a tarefa e a descrição.")

# Função para alterar o status
def alterar_status():
    try:
        selecionado = tree.selection()[0]
        tarefa = tree.item(selecionado)["values"][0]
        novo_status = combo_status.get()
        if novo_status:
            for item in roadmap:
                if item["Tarefa"] == tarefa:
                    item["Status"] = novo_status
                    cursor.execute("UPDATE roadmap SET status = ? WHERE tarefa = ?", (novo_status, tarefa))
                    conn.commit()
                    break
            atualizar_tabela()
            messagebox.showinfo("Sucesso", "Status atualizado com sucesso!")
        else:
            messagebox.showwarning("Seleção de status", "Por favor, selecione um status.")
    except IndexError:
        messagebox.showwarning("Seleção necessária", "Por favor, selecione um item para alterar o status.")

# Função para remover uma tarefa
def remover_tarefa():
    try:
        selecionado = tree.selection()[0]
        tarefa = tree.item(selecionado)["values"][0]
        global roadmap
        roadmap = [item for item in roadmap if item["Tarefa"] != tarefa]
        cursor.execute("DELETE FROM roadmap WHERE tarefa = ?", (tarefa,))
        conn.commit()
        atualizar_tabela()
        messagebox.showinfo("Sucesso", "Tarefa removida com sucesso!")
    except IndexError:
        messagebox.showwarning("Seleção necessária", "Por favor, selecione uma tarefa para remover.")

# Função para salvar em PDF
def salvar_pdf():
    filepath = asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if filepath:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Roadmap de Estudos", ln=True, align="C")
        pdf.ln(10)
        for item in roadmap:
            pdf.cell(0, 10, txt=f"Tarefa: {item['Tarefa']}", ln=True)
            pdf.cell(0, 10, txt=f"Status: {item['Status']}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Descrição: {item['Descrição']}")
            pdf.ln(5)
        pdf.output(filepath)
        messagebox.showinfo("Sucesso", "PDF salvo com sucesso!")

# Função para exibir o roadmap completo
def mostrar_roadmap():
    janela_roadmap = tk.Toplevel(root)
    janela_roadmap.title("Visualização do Roadmap Completo")
    text_roadmap = tk.Text(janela_roadmap, wrap="word")
    text_roadmap.pack(fill="both", expand=True, padx=10, pady=10)

    # Exibir dados no widget de texto
    for item in roadmap:
        text_roadmap.insert(tk.END, f"Tarefa: {item['Tarefa']}\n")
        text_roadmap.insert(tk.END, f"Status: {item['Status']}\n")
        text_roadmap.insert(tk.END, f"Descrição: {item['Descrição']}\n")
        text_roadmap.insert(tk.END, "-" * 50 + "\n")

    text_roadmap.config(state="disabled")  # Impedir edição do texto

# Interface gráfica
root = tk.Tk()
root.title("Roadmap de Estudos")

# Frame de Pesquisa
frame_pesquisa = tk.Frame(root)
frame_pesquisa.pack(pady=10)
tk.Label(frame_pesquisa, text="Pesquisar:").pack(side="left")
entry_pesquisa = tk.Entry(frame_pesquisa)
entry_pesquisa.pack(side="left", padx=5)
tk.Button(frame_pesquisa, text="Pesquisar", command=pesquisar).pack(side="left", padx=5)

# Tabela
columns = ("Tarefa", "Status", "Descrição")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("Tarefa", text="Tarefa")
tree.heading("Status", text="Status")
tree.heading("Descrição", text="Descrição (resumo)")
tree.pack(pady=10, fill="both", expand=True)

# Frame de Adição
frame_adicionar = tk.Frame(root)
frame_adicionar.pack(pady=10)
tk.Label(frame_adicionar, text="Nova Tarefa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_tarefa = tk.Entry(frame_adicionar, width=50)
entry_tarefa.grid(row=0, column=1, padx=5, pady=5)
tk.Label(frame_adicionar, text="Descrição:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
text_descricao = tk.Text(frame_adicionar, width=50, height=5)
text_descricao.grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame_adicionar, text="Adicionar", command=adicionar_tarefa).grid(row=2, column=1, pady=10, sticky="e")

# Frame de Alteração e Remoção
frame_alterar = tk.Frame(root)
frame_alterar.pack(pady=10)
tk.Label(frame_alterar, text="Novo Status:").pack(side="left")
combo_status = ttk.Combobox(frame_alterar, values=["Pendente", "Em Progresso", "Concluído"])
combo_status.pack(side="left", padx=5)
tk.Button(frame_alterar, text="Alterar Status", command=alterar_status).pack(side="left", padx=5)
tk.Button(frame_alterar, text="Remover", command=remover_tarefa).pack(side="left", padx=5)

# Botões para Salvar e Visualizar
frame_acao = tk.Frame(root)
frame_acao.pack(pady=10)
tk.Button(frame_acao, text="Salvar em PDF", command=salvar_pdf).pack(side="left", padx=10)
tk.Button(frame_acao, text="Visualizar Roadmap", command=mostrar_roadmap).pack(side="left", padx=10)

# Carregar dados na tabela
atualizar_tabela()

root.mainloop()

# Fechar conexão com o banco de dados ao finalizar
conn.close()
