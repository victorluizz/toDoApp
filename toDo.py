import flet as ft
import sqlite3

class ToDo:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.bgcolor = ft.colors.BLUE_GREY
        self.page.window_width = 350
        self.page.window_height = 450
        self.page.window_resizable = False #Impede que a tela seja redimensionada
        self.page.window_always_on_top = True #Deixa a tela sempre por cima, sem minimizar. Ajuda para você visualizar o que tá construindo
        self.page.title = "ToDo App"
        self.task = ''
        self.view = 'all'
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks(nome, progresso)')
        self.resultado=self.db_execute('SELECT * FROM tasks')
        self.main_page()
        
    def db_execute(self, query, parametros = []):
        with sqlite3.connect('database.db') as con: #Serve para abrir uma conexão com o banco de dados sempre que precisar usar o banco
            cur = con.cursor()
            cur.execute(query, parametros)
            con.commit()
            return cur.fetchall()
        
    def set_value(self, evento):
        self.task = evento.control.value
        
    def addTask(self, evento, input_task):
        nome = self.task #Cada vez que eu digito qualquer coisa na caixinha de texto das tarefas, ele é adicionado a variável "task"
        progresso = "incompleto"
        
        if nome:
            self.db_execute(query='INSERT INTO tasks VALUES (?, ?)', parametros=[nome, progresso])
            input_task.value=''
            self.resultado=self.db_execute('SELECT * FROM tasks') #Exibindo todas as taks da tabela "tasks"
            self.atualizar_lista_tasks()

    def atualizar_lista_tasks(self):
        tasks = self.tasks_container()
        self.page.controls.pop() #Remove a primeira task atual e sobrescreve com os elementos atualizados
        self.page.add(tasks)
        self.page.update()
    
    def checked(self, evento):
        isChecked = evento.control.value
        label = evento.control.label

        if isChecked:
            self.db_execute('UPDATE tasks SET progresso = "completo" WHERE nome = ?', parametros=[label])
        else:
            self.db_execute('UPDATE tasks SET progresso = "incompleto" WHERE nome = ?', parametros=[label])

        if self.view == 'all':
            self.resultado = self.db_execute('SELECT * FROM tasks')
        else:
            self.resultado = self.db_execute('SELECT * FROM tasks WHERE progresso = ?', parametros=[self.view])
        self.atualizar_lista_tasks()

    def tasks_container(self):
        return ft.Container(
            height=self.page.height * 0.8,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Checkbox(
                                label=res[0], 
                                on_change=self.checked,
                                value=True if res[1] == 'completo' else False
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                on_click=self.removerTask,
                                data=res[0]
                            ),
                            ft.IconButton(
                                icon=ft.icons.PAUSE,
                                on_click=self.pausarTask,
                                data=res[0]
                            )
                        ]
                    )
                    for res in self.resultado if res
                ]
            )    
        )
    
    def pausarTask(self, evento):
        taskPausada = evento.control.data
        self.db_execute('UPDATE tasks SET progresso = "pausada" WHERE nome = ?', parametros=[taskPausada])
        if self.view == 'all':
            self.resultado=self.db_execute('SELECT * FROM tasks')
        else:
            self.resultado=self.db_execute('SELECT * FROM tasks WHERE progresso = ?', parametros=[self.view])
        self.atualizar_lista_tasks()
    
    def removerTask(self, evento):
        taskRemocao = evento.control.data
        self.db_execute('DELETE FROM tasks WHERE nome = ?', parametros=[taskRemocao])
        if self.view == 'all':
            self.resultado=self.db_execute('SELECT * FROM tasks')
        else:
            self.resultado=self.db_execute('SELECT * FROM tasks WHERE progresso = ?', parametros=[self.view])
        self.atualizar_lista_tasks()

    def tabsChanged(self, evento):
        if evento.control.selected_index == 0:
            self.resultado = self.db_execute('SELECT * FROM tasks')
            self.view = 'all'
        elif evento.control.selected_index==1:
            self.resultado = self.db_execute('SELECT * FROM tasks WHERE progresso = "incompleto"')
            self.view = 'incompleto'
        elif evento.control.selected_index==2:
            self.resultado = self.db_execute('SELECT * FROM tasks WHERE progresso = "completo"')
            self.view = 'completo'
        elif evento.control.selected_index==3:
            self.resultado = self.db_execute('SELECT * FROM tasks WHERE progresso = "pausada"')
            self.view = 'pausada'
        
        self.atualizar_lista_tasks()


    def main_page(self):
        input_task = ft.TextField(hint_text= "Digite uma tarefa", expand=True, on_change=self.set_value) #Cria a caixinha de texto para inserir a tarefa.
        
        input_bar = ft.Row(
            controls=[
                input_task,
                ft.FloatingActionButton(
                    icon= ft.icons.ADD,
                    on_click=lambda evento: self.addTask(evento, input_task)
                )
            ]
        )
        
        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabsChanged, #Significa que a aba "Todos" é que vai estar selecionada por padrão, já que ela é o indíce 0 na lista de tabs
            tabs=[
                ft.Tab(text="Todos"),
                ft.Tab(text="Em andamento"),
                ft.Tab(text="Finalizadas"),
                ft.Tab(text="Pausadas")
            ]
        )
        
        tasks = self.tasks_container()
        self.page.add(input_bar, tabs, tasks) #Serve para colocar tudo que você criou na sua tela
        
    
ft.app(target= ToDo)
        

