"""Espaço de estados: as 40 casas, preços, aluguéis e cartas (edição americana)."""

N = 40

NOMES = [
    "Partida (GO)", "Avenida Mediterranea", "Cofre Comunitario", "Avenida Baltica",
    "Imposto de Renda", "Reading Railroad", "Avenida Oriental", "Sorte",
    "Avenida Vermont", "Avenida Connecticut", "Cadeia / Só Visitando", "Praca St. Charles",
    "Companhia Eletrica", "Avenida States", "Avenida Virginia", "Pennsylvania Railroad",
    "Praca St. James", "Cofre Comunitario", "Avenida Tennessee", "Avenida New York",
    "Estacionamento Livre", "Avenida Kentucky", "Sorte", "Avenida Indiana",
    "Avenida Illinois", "B&O Railroad", "Avenida Atlantic", "Avenida Ventnor",
    "Companhia de Agua", "Jardins Marvin", "Va para a Cadeia", "Avenida Pacifico",
    "Avenida Carolina do Norte", "Cofre Comunitario", "Avenida Pennsylvania",
    "Short Line Railroad", "Sorte", "Imposto de Luxo", "Praca Park Place", "Avenida Boardwalk",
]

GO = 0
CADEIA = 10
VA_PARA_CADEIA = 30
SORTE_IDX = [7, 22, 36]
COFRE_IDX = [2, 17, 33]
FERROVIAS = [5, 15, 25, 35]
UTILIDADES = [12, 28]

PRECOS = {
    1: 60, 3: 60, 5: 200, 6: 100, 8: 100, 9: 120, 11: 140, 12: 150,
    13: 140, 14: 160, 15: 200, 16: 180, 18: 180, 19: 200, 21: 220,
    23: 220, 24: 240, 25: 200, 26: 260, 27: 260, 28: 150, 29: 280,
    31: 300, 32: 300, 34: 320, 35: 200, 38: 350, 39: 400,
}

GRUPOS = {
    "Marrom": [1, 3],
    "Azul Claro": [6, 8, 9],
    "Rosa": [11, 13, 14],
    "Laranja": [16, 18, 19],
    "Vermelho": [21, 23, 24],
    "Amarelo": [26, 27, 29],
    "Verde": [31, 32, 34],
    "Azul Escuro": [38, 39],
    "Ferrovia": FERROVIAS,
    "Utilidade": UTILIDADES,
}

GRUPO_COR = {casa: grupo for grupo, casas in GRUPOS.items() for casa in casas}

CUSTO_CASA = {
    "Marrom": 50, "Azul Claro": 50, "Rosa": 100, "Laranja": 100,
    "Vermelho": 150, "Amarelo": 150, "Verde": 200, "Azul Escuro": 200,
}

# casa: (sem casas, 1, 2, 3, 4 casas, hotel)
ALUGUEIS = {
    1: (2, 10, 30, 90, 160, 250), 3: (4, 20, 60, 180, 320, 450),
    6: (6, 30, 90, 270, 400, 550), 8: (6, 30, 90, 270, 400, 550),
    9: (8, 40, 100, 300, 450, 600),
    11: (10, 50, 150, 450, 625, 750), 13: (10, 50, 150, 450, 625, 750),
    14: (12, 60, 180, 500, 700, 900),
    16: (14, 70, 200, 550, 750, 950), 18: (14, 70, 200, 550, 750, 950),
    19: (16, 80, 220, 600, 800, 1000),
    21: (18, 90, 250, 700, 875, 1050), 23: (18, 90, 250, 700, 875, 1050),
    24: (20, 100, 300, 750, 925, 1100),
    26: (22, 110, 330, 800, 975, 1150), 27: (22, 110, 330, 800, 975, 1150),
    29: (24, 120, 360, 850, 1025, 1200),
    31: (26, 130, 390, 900, 1100, 1275), 32: (26, 130, 390, 900, 1100, 1275),
    34: (28, 150, 450, 1000, 1200, 1400),
    38: (35, 175, 500, 1100, 1300, 1500), 39: (50, 200, 600, 1400, 1700, 2000),
}


def mais_proxima(idx, alvos, n=N):
    """Primeiro alvo encontrado andando para a frente a partir de idx."""
    return min(((a - idx) % n, a) for a in alvos)[1]


def destinos_sorte(casa):
    """As 10 cartas de Sorte (de 16) que movem o jogador, partindo de `casa`."""
    ferrovia = mais_proxima(casa, FERROVIAS)
    companhia = mais_proxima(casa, UTILIDADES)
    return [GO, 24, 11, companhia, ferrovia, ferrovia, (casa - 3) % N, CADEIA, 5, 39]


DESTINOS_COFRE = [GO, CADEIA]
