import tkinter as tk
from binance.client import Client
import os 

# Substitua suas chaves de API aqui
api_key = os.getenv("KEY_BINANCE")
api_secret = os.getenv("SECRET_BINANCE")

# Inicialize o cliente da Binance
cliente_binance = Client(api_key, api_secret)

# Função para obter informações de tamanho de lote para um ativo
def consultar_lote(codigo_ativo):
    exchange_info = cliente_binance.get_exchange_info()
    symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == codigo_ativo), None)
    if symbol_info:
        lot_size_info = next((f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'), None)
        if lot_size_info:
            return lot_size_info
    return None

# Função para obter o preço do ativo
def obter_preco_cripto(codigo_ativo):
    try:
        # Tentar o símbolo diretamente
        preco = cliente_binance.get_symbol_ticker(symbol=codigo_ativo)['price']
    except:
        # Se falhar, adicionar USDT ao final e tentar novamente
        simbolo = f"{codigo_ativo}USDT"
        preco = cliente_binance.get_symbol_ticker(symbol=simbolo)['price']
    return float(preco)

# Função para verificar se o símbolo é válido
def validar_simbolo(codigo_ativo):
    exchange_info = cliente_binance.get_exchange_info()
    return any(s['symbol'] == codigo_ativo for s in exchange_info['symbols'])

# Função para buscar e exibir informações de lote
def buscar_lote():
    codigo_ativo = entry_codigo_ativo.get()
    if codigo_ativo:
        if not validar_simbolo(codigo_ativo):
            lbl_resultado.config(text=f"Símbolo inválido: {codigo_ativo}.")
            return
        
        lote_info = consultar_lote(codigo_ativo)
        preco_ativo = obter_preco_cripto(codigo_ativo)
        if lote_info and preco_ativo:
            resultado_texto = (f"Preço atual de {codigo_ativo}: ${preco_ativo:.2f}\n\n"
                               f"Tamanho mínimo do lote para {codigo_ativo}: {lote_info['minQty']}\n"
                               f"Tamanho máximo do lote para {codigo_ativo}: {lote_info['maxQty']}\n"
                               f"Incremento de tamanho do lote para {codigo_ativo}: {lote_info['stepSize']}")
            lbl_resultado.config(text=resultado_texto)
        else:
            lbl_resultado.config(text=f"Não foi possível obter informações de tamanho de lote para {codigo_ativo}.")
    else:
        lbl_resultado.config(text="Por favor, insira o código do ativo.")

# Criação da interface gráfica
root = tk.Tk()
root.title("Consulta de Tamanho de Lote")

# Rótulo e campo de entrada para o código do ativo
tk.Label(root, text="Código do Ativo:").grid(row=0, column=0, padx=10, pady=10)
entry_codigo_ativo = tk.Entry(root)
entry_codigo_ativo.grid(row=0, column=1, padx=10, pady=10)

# Botão para buscar as informações de lote
btn_buscar = tk.Button(root, text="Buscar Lote", command=buscar_lote)
btn_buscar.grid(row=1, columnspan=2, pady=10)

# Rótulo para exibir o resultado
lbl_resultado = tk.Label(root, text="", justify=tk.LEFT)
lbl_resultado.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()


