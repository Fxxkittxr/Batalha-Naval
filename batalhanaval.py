import tkinter as tk
from tkinter import messagebox
import random

class BatalhaNaval:
    def __init__(self, root):
        self.root = root
        self.root.title("Batalha Naval")
        
        self.navios = [("Porta-aviões", 5), 
                       ("Encouraçado", 4), 
                       ("Cruzador", 3), 
                       ("Submarino", 3), 
                       ("Hidroavião", 2)]
        
        # Estado das grelhas (usuario e IA)
        self.estado_grelha_usuario = [[" " for _ in range(10)] for _ in range(10)]
        self.estado_grelha_ia = [[" " for _ in range(10)] for _ in range(10)]
        
        # Variáveis para controle do jogo
        self.posicionando_navios = True
        self.indice_navio_atual = 0
        self.jogador_atual = "Usuário"
        self.direcao_navio = "horizontal"  # Direção inicial

        # Heurística e estado da IA
        self.ia_acertou = False
        self.ia_proximos_alvos = []  # Posições a serem atacadas pela IA após acertar um navio
        self.ia_ultimas_jogadas = []  # Histórico de jogadas da IA

        # Botões da grelha
        self.botoes_usuario = []
        self.botoes_ia = []

        # Limitar janela
        self.root.geometry("840x680")  # Define o tamanho fixo da janela
        self.root.resizable(False, False)  # Impede que a janela seja redimensionada

        # Criação das grelhas do usuário e da IA
        self.create_grid("Usuário", 0, 0, True)
        self.create_grid("IA", 0, 1, False)

        # Posicionar automaticamente navios da IA
        self.posicionar_navios_ia()

        # Solicitar posicionamento de navios para o usuário
        self.solicitar_posicionamento_navios()

        # Botão para trocar a direção do navio, exibindo a direção atual
        self.trocar_direcao_button = tk.Button(root, text=f"Direção: {self.direcao_navio.capitalize()}", command=self.trocar_direcao)
        self.trocar_direcao_button.grid(row=2, column=0, columnspan=2)

        # Criação da seção de regras com scroll
        self.create_regras_section()

    def create_regras_section(self):
        regras_frame = tk.Frame(self.root)
        regras_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

        # Canvas para permitir a rolagem
        canvas = tk.Canvas(regras_frame, width=580)  # Remover altura fixa
        self.regras_content = tk.Frame(canvas)

        # Configurar o canvas
        self.regras_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.regras_content, anchor="nw")

        # Adicionar regras ao Frame de regras
        regras_texto = (
            "Regras do Jogo:\n"
            "1. Posicione seus navios no tabuleiro.\n"
            "2. O jogo inicia com o jogador atirando na grelha da Inteligência Artificial tentando acertar um navio.\n"
            "3. O jogo alterna entre a vez do jogador e a IA.\n"
            "4. O primeiro a afundar todos os navios do adversário vence.\n"
            "5. Navios não podem ser posicionados em diagonal e não podem se sobrepor.\n"
            "6. Cada tiro bem-sucedido é marcado em vermelho, e tiros errados são marcados em branco."
        )
        # Criar o Label de regras com bordas e cor de fundo
        regras_label = tk.Label(
            self.regras_content,
            text=regras_texto,
            justify="left",
            font=("Helvetica", 10),
            bg="light gray",  # Cor de fundo
            fg="black",  # Cor do texto
            borderwidth=1,  # Espessura da borda
            relief="solid",  # Estilo da borda
            padx=10,  # Preenchimento interno no eixo x
            pady=10,  # Preenchimento interno no eixo y
            wraplength=570,  # Ajuste o wraplength para caber no canvas
            width = 70,
            height = 8
    )
        
        regras_label.pack(fill="both", expand=True)  # Ocupar todo o espaço disponível

        # Adicionando canvas ao frame
        canvas.pack(side="left", fill="both", expand=True)

    def create_grid(self, title, row, col, usuario):
        
        frame = tk.Frame(self.root)
        frame.grid(row=row, column=col, padx=20, pady=20)

        title_label = tk.Label(frame, text=title, font=("Helvetica", 16))
        title_label.pack()

        grid_frame = tk.Frame(frame)
        grid_frame.pack()

        botoes_grid = []
        for i in range(10):
            linha_botoes = []
            for j in range(10):
                button = tk.Button(grid_frame, 
                                   width=4, 
                                   height=2, 
                                   bg='light blue' if usuario else 'light pink', 
                                   command=lambda r=i, c=j: 
                                   self.posicionar_ou_atirar(r, c, usuario)
                                   )
                button.grid(row=i, column=j)
                linha_botoes.append(button)
            botoes_grid.append(linha_botoes)

        if usuario:
            self.botoes_usuario = botoes_grid
        else:
            self.botoes_ia = botoes_grid

    def solicitar_posicionamento_navios(self):
        self.posicionando_navios = True
        self.indice_navio_atual = 0
        self.direcao_navio = "horizontal"  # Resetar a direção ao solicitar novo posicionamento
        self.posicionar_navio()

    def posicionar_navio(self):
        if self.indice_navio_atual < len(self.navios):
            nome, tamanho = self.navios[self.indice_navio_atual]
            messagebox.showinfo("Posicionamento", f"Posicione o {nome} (tamanho {tamanho})")
        else:
            self.posicionando_navios = False
            messagebox.showinfo("Pronto!", "Todos os navios posicionados. Bom jogo...")

    def trocar_direcao(self):
        if self.indice_navio_atual < len(self.navios):
            if self.direcao_navio == "horizontal":
                self.direcao_navio = "vertical"
            else:
                self.direcao_navio = "horizontal"
            
            # Atualiza o texto do botão para mostrar a direção atual
            self.trocar_direcao_button.config(text=f"Direção: {self.direcao_navio.capitalize()}")

    def posicionar_ou_atirar(self, linha, coluna, usuario):
        if self.posicionando_navios and usuario:
            self.posicionar_navio_usuario(linha, coluna)
        elif not usuario and not self.posicionando_navios:
            self.atirar(linha, coluna)

    def posicionar_navio_usuario(self, linha, coluna):
        if self.indice_navio_atual < len(self.navios):
            nome, tamanho = self.navios[self.indice_navio_atual]

            if self.direcao_navio == "horizontal":
                if coluna + tamanho <= 10:  
                    for i in range(tamanho):
                        self.estado_grelha_usuario[linha][coluna + i] = "N"
                        self.botoes_usuario[linha][coluna + i].config(bg="black")
                    self.indice_navio_atual += 1
                    self.posicionar_navio()
                else:
                    messagebox.showwarning("Aviso", "Posição inválida. O navio não cabe na linha escolhida.")
            else:  # Direção vertical
                if linha + tamanho <= 10:
                    for i in range(tamanho):
                        self.estado_grelha_usuario[linha + i][coluna] = "N"
                        self.botoes_usuario[linha + i][coluna].config(bg="black")
                    self.indice_navio_atual += 1
                    self.posicionar_navio()
                else:
                    messagebox.showwarning("Aviso", "Posição inválida. O navio não cabe na coluna escolhida.")

    def posicionar_navios_ia(self):
        for navio, tamanho in self.navios:
            posicionado = False
            while not posicionado:
                orientacao = random.choice(["horizontal", "vertical"])  # Limitar IA para colocar navios em linha
                if orientacao == "horizontal":
                    linha = random.randint(0, 9)
                    coluna = random.randint(0, 9 - tamanho)
                    if all(self.estado_grelha_ia[linha][coluna + i] == " " for i in range(tamanho)):
                        for i in range(tamanho):
                            self.estado_grelha_ia[linha][coluna + i] = "N"
                        posicionado = True
                else:
                    linha = random.randint(0, 9 - tamanho)
                    coluna = random.randint(0, 9)
                    if all(self.estado_grelha_ia[linha + i][coluna] == " " for i in range(tamanho)):
                        for i in range(tamanho):
                            self.estado_grelha_ia[linha + i][coluna] = "N"
                        posicionado = True

    def atirar(self, linha, coluna):
        if self.estado_grelha_ia[linha][coluna] == "N":
            self.estado_grelha_ia[linha][coluna] = "X"
            self.botoes_ia[linha][coluna].config(bg="red")
        elif self.estado_grelha_ia[linha][coluna] == " ":
            self.estado_grelha_ia[linha][coluna] = "-"
            self.botoes_ia[linha][coluna].config(bg="white")

        if self.verificar_fim_jogo("IA"):
            self.fim_jogo("Vitória!", "Você venceu! Todos os navios inimigos foram afundados.")
        else:
            self.ataque_ia()

    def ataque_ia(self):
        if self.ia_proximos_alvos:
            linha, coluna = self.ia_proximos_alvos.pop(0)  # Ataca o próximo alvo
        else:
            linha, coluna = random.randint(0, 9), random.randint(0, 9)
            while (linha, coluna) in self.ia_ultimas_jogadas:
                linha, coluna = random.randint(0, 9), random.randint(0, 9)
        
        self.ia_ultimas_jogadas.append((linha, coluna))

        if self.estado_grelha_usuario[linha][coluna] == "N":
            self.estado_grelha_usuario[linha][coluna] = "X"
            self.botoes_usuario[linha][coluna].config(bg="red")
            self.ia_acertou = True
            self.adicionar_proximos_alvos(linha, coluna)
        else:
            self.estado_grelha_usuario[linha][coluna] = "-"
            self.botoes_usuario[linha][coluna].config(bg="white")

        if self.verificar_fim_jogo("Usuário"):
            self.fim_jogo("Derrota!", "Você perdeu! Todos os seus navios foram afundados.")

    def adicionar_proximos_alvos(self, linha, coluna):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x, y = linha + dx, coluna + dy
            if 0 <= x < 10 and 0 <= y < 10 and (x, y) not in self.ia_ultimas_jogadas:
                self.ia_proximos_alvos.append((x, y))

    def verificar_fim_jogo(self, jogador):
        if jogador == "Usuário":
            return all(cell != "N" for row in self.estado_grelha_usuario for cell in row)
        else:
            return all(cell != "N" for row in self.estado_grelha_ia for cell in row)

    def fim_jogo(self, titulo, mensagem):
        resposta = messagebox.askyesno(titulo, f"{mensagem}\nDeseja jogar novamente?")
        if resposta:
            self.reiniciar_jogo()
        else:
            self.root.destroy()

    def reiniciar_jogo(self):
        self.root.destroy()
        root = tk.Tk()
        app = BatalhaNaval(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = BatalhaNaval(root)
    root.mainloop()
