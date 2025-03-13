import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime


class StudyRoadmapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roadmap de Estudos")

        # Estrutura para armazenar as tarefas
        self.tasks = []  # Lista de dicionários com tarefas

        # Layout da interface
        self.create_widgets()

    def create_widgets(self):
        # Título
        self.title_label = tk.Label(self.root, text="Roadmap de Estudos", font=("Arial", 18))
        self.title_label.grid(row=0, column=0, columnspan=4, pady=10)

        # Labels para Adicionar Tarefa
        self.task_label = tk.Label(self.root, text="Tarefa:")
        self.task_label.grid(row=1, column=0)

        self.task_entry = tk.Entry(self.root)
        self.task_entry.grid(row=1, column=1)

        self.date_label = tk.Label(self.root, text="Data de Conclusão:")
        self.date_label.grid(row=2, column=0)

        self.date_entry = tk.Entry(self.root)
        self.date_entry.grid(row=2, column=1)

        # Botões
        self.add_button = tk.Button(self.root, text="Adicionar Tarefa", command=self.add_task)
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.show_roadmap_button = tk.Button(self.root, text="Mostrar Roadmap", command=self.show_roadmap)
        self.show_roadmap_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.show_graph_button = tk.Button(self.root, text="Mostrar Gráfico de Progresso", command=self.show_graph)
        self.show_graph_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.search_button = tk.Button(self.root, text="Pesquisar Tarefa", command=self.search_task)
        self.search_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.save_pdf_button = tk.Button(self.root, text="Salvar em PDF", command=self.save_pdf)
        self.save_pdf_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Tabela para exibir tarefas
        self.treeview = ttk.Treeview(self.root, columns=("Tarefa", "Data de Conclusão", "Status"), show="headings")
        self.treeview.heading("Tarefa", text="Tarefa")
        self.treeview.heading("Data de Conclusão", text="Data de Conclusão")
        self.treeview.heading("Status", text="Status")
        self.treeview.grid(row=8, column=0, columnspan=2, pady=10)

    def add_task(self):
        task_name = self.task_entry.get()
        due_date = self.date_entry.get()

        if task_name and due_date:
            # Validando a data
            try:
                datetime.datetime.strptime(due_date, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use AAAA-MM-DD.")
                return

            task = {"Tarefa": task_name, "Data de Conclusão": due_date, "Status": "Não Iniciada"}
            self.tasks.append(task)
            self.update_task_list()
            messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")
        else:
            messagebox.showerror("Erro", "Preencha todos os campos.")

    def update_task_list(self):
        # Atualiza a lista de tarefas na Treeview
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        for task in self.tasks:
            self.treeview.insert("", "end", values=(task["Tarefa"], task["Data de Conclusão"], task["Status"]))

    def show_roadmap(self):
        # Mostrar um simples roadmap de todas as tarefas
        roadmap_window = tk.Toplevel(self.root)
        roadmap_window.title("Roadmap de Estudos")

        # Criando uma lista das tarefas no roadmap
        roadmap_text = tk.Text(roadmap_window, width=50, height=15)
        roadmap_text.pack(padx=10, pady=10)

        for task in self.tasks:
            roadmap_text.insert(tk.END, f"Tarefa: {task['Tarefa']}\n")
            roadmap_text.insert(tk.END, f"Data de Conclusão: {task['Data de Conclusão']}\n")
            roadmap_text.insert(tk.END, f"Status: {task['Status']}\n\n")

        roadmap_text.config(state=tk.DISABLED)

    def show_graph(self):
        # Gerar gráfico de progresso baseado no status das tarefas
        completed = sum(1 for task in self.tasks if task["Status"] == "Concluída")
        not_started = sum(1 for task in self.tasks if task["Status"] == "Não Iniciada")
        in_progress = len(self.tasks) - completed - not_started

        # Plotar gráfico de barras
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Concluídas", "Em Andamento", "Não Iniciadas"], [completed, in_progress, not_started],
               color=['green', 'orange', 'red'])
        ax.set_title('Progresso do Roadmap de Estudos')
        ax.set_ylabel('Número de Tarefas')

        # Mostrar gráfico no Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().grid(row=9, column=0, columnspan=2)
        canvas.draw()

    def search_task(self):
        search_term = simpledialog.askstring("Pesquisar", "Digite o nome da tarefa ou parte dele:")
        if search_term:
            found_tasks = [task for task in self.tasks if search_term.lower() in task["Tarefa"].lower()]
            if found_tasks:
                search_results_window = tk.Toplevel(self.root)
                search_results_window.title("Resultados da Pesquisa")

                search_results_text = tk.Text(search_results_window, width=50, height=15)
                search_results_text.pack(padx=10, pady=10)
                for task in found_tasks:
                    search_results_text.insert(tk.END, f"Tarefa: {task['Tarefa']}\n")
                    search_results_text.insert(tk.END, f"Data de Conclusão: {task['Data de Conclusão']}\n")
                    search_results_text.insert(tk.END, f"Status: {task['Status']}\n\n")
                search_results_text.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Pesquisa", "Nenhuma tarefa encontrada.")

    def save_pdf(self):
        file_name = "roadmap_estudos.pdf"
        c = canvas.Canvas(file_name, pagesize=letter)

        c.drawString(100, 750, "Relatório do Roadmap de Estudos")
        c.drawString(100, 730, f"Data de Geração: {datetime.datetime.now().strftime('%Y-%m-%d')}")

        y_position = 700
        for task in self.tasks:
            c.drawString(100, y_position,
                         f"Tarefa: {task['Tarefa']} | Data de Conclusão: {task['Data de Conclusão']} | Status: {task['Status']}")
            y_position -= 20

        c.save()
        messagebox.showinfo("Sucesso", f"Relatório salvo em PDF: {file_name}")


# Rodando a aplicação
root = tk.Tk()
app = StudyRoadmapApp(root)
root.mainloop()
