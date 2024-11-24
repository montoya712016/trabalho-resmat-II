import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# Função para calcular o momento de inércia para uma seção retangular
def momento_inercia_retangular(b, h):
    return (b * h**3) / 12  # mm^4

# Função para calcular a tensão de flexão máxima
def calcular_tensao_flexao(F, L, b, h):
    M = (F * L) / 4  # Momento fletor máximo (N·mm)
    I = momento_inercia_retangular(b, h)  # Momento de inércia (mm^4)
    c = h / 2  # Distância do eixo neutro à borda da seção (mm)
    return (M * c) / I  # Tensão de flexão máxima (MPa)

# Configurações do material Policarbonato
policarbonato = {
    "nome": "Policarbonato",
    "Ef": 274,
    "sigma_0.2": 21.8,
    "h": 6.11,
    "b": 13.58,
    "arquivo": "Mecanicos.2.TXT"
}

# Comprimento entre apoios (mm)
L = 127

# Obter o diretório onde o script está localizado
caminho_codigo = os.path.dirname(os.path.abspath(__file__))

# Criar figura e eixos principais
fig, ax1 = plt.subplots(figsize=(10, 6))

# Dados do material Policarbonato
b, h = policarbonato["b"], policarbonato["h"]
arquivo = os.path.join(caminho_codigo, policarbonato["arquivo"])

if not os.path.exists(arquivo):
    print(f"Arquivo não encontrado: {arquivo}")
else:
    # Leia o arquivo ignorando o cabeçalho inicial
    df = pd.read_csv(arquivo, skiprows=4, names=["Deformacao (mm)", "Forca (N)"])
    df["Forca (N)"] = pd.to_numeric(df["Forca (N)"], errors="coerce")
    df["Deformacao (mm)"] = pd.to_numeric(df["Deformacao (mm)"], errors="coerce")
    df = df.dropna()
    df["Tensao (MPa)"] = df["Forca (N)"].apply(lambda F: calcular_tensao_flexao(F, L, b, h))
    ax1.plot(df["Deformacao (mm)"], df["Tensao (MPa)"], label="Modelo Teórico")

# Limitar o eixo X até 10 mm
ax1.set_xlim(0, 10)

# Carregar a curva experimental
arquivo_experimental = os.path.join(caminho_codigo, "Default Dataset.csv")
data = pd.read_csv(arquivo_experimental, sep=';', header=None, names=['X', 'Y'], decimal=',')
data['X'] = data['X'].astype(float)
data['Y'] = data['Y'].astype(float)

# Aplicar transformação linear ao eixo X experimental
a = 6.44 / 28.1143
b = 0
data['X_transformado'] = a * data['X'] + b
ax1.plot(data['X_transformado'], data['Y'], color='r', linestyle='--', label="Curva Experimental")

# Interpolação da curva experimental no eixo X teórico
x_teorico = df["Deformacao (mm)"]
y_experimental_interpolado = np.interp(x_teorico, data["X_transformado"], data["Y"])

# Calcular erros
erro_absoluto = np.abs(df["Tensao (MPa)"] - y_experimental_interpolado)
erro_percentual = (erro_absoluto / df["Tensao (MPa)"]) * 100

# Calcular máximos e erro percentual entre os máximos
max_teorico = df["Tensao (MPa)"].max()
x_max_teorico = df.loc[df["Tensao (MPa)"].idxmax(), "Deformacao (mm)"]
max_experimental = data["Y"].max()
x_max_experimental = data.loc[data["Y"].idxmax(), "X_transformado"]

erro_percentual_maximos = (abs(max_teorico - max_experimental) / max_teorico) * 100

# Exibir métricas de erro
mae = erro_absoluto.mean()
mape = erro_percentual.mean()

print(f"Erro Médio Absoluto (MAE): {mae:.4f} MPa")
print(f"Erro Médio Percentual (MAPE): {mape:.2f} %")
print(f"Máximo Teórico: {max_teorico:.2f} MPa em {x_max_teorico:.2f} mm")
print(f"Máximo Experimental: {max_experimental:.2f} MPa em {x_max_experimental:.2f} mm")
print(f"Erro Percentual entre os Máximos: {erro_percentual_maximos:.2f} %")

# Configurações do gráfico
ax1.set_xlabel("Deformação (mm)")
ax1.set_ylabel("Tensão de Flexão (MPa)")
ax1.grid(True, linestyle='--', alpha=0.6)
plt.title("Curva Tensão x Deformação - Policarbonato")
plt.legend(loc="lower right")
plt.show()
