## NEGOCIA CRIPTO 
## REGRA MEDIA RAPIDA (7) E LENTA (40)
## ABRE ORDEM OCO JUNTO DA OPERAÇÃO
## TEM FORMULARIO PARA INSERÇÃO DE DADOS - MANUAL - SOLICITA CONFIRMAÇÃO PARA ABRIR ORDEM
## ALS - COPILOT - 27/01/2025
## 

import win32com.client as win32
import pandas as pd
import requests
from dotenv import load_dotenv
import tkinter as tk
from binance.client import Client
import os 
import datetime

# Substitua suas chaves de API aqui
api_key = os.getenv("KEY_BINANCE")
api_secret = os.getenv("SECRET_BINANCE")

# Inicialize o cliente da Binance
cliente_binance = Client(api_key, api_secret)

def enviar_email_outlook(mensagem):
    outlook = win32.Dispatch('outlook.application')
    email = outlook.CreateItem(0)
    email.To = "alscentury@gmail.com"
    email.Subject = "Informações de Cripto"
    email.Body = mensagem
    email.Send()
    print("E-mail enviado pelo Outlook.")

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

def obter_taxa_cambio():
    try:
        resposta = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        dados = resposta.json()
        return dados['rates']['BRL']
    except Exception as e:
        print(f"Erro ao obter a taxa de câmbio: {e}")
        return None
def calcular_lucro_potencial(event):
    try:
        valor_atual = float(entry_valor_atual_brl.get())
        percentual_ganho = float(entry_percentual_ganho.get())
        lucro_potencial = valor_atual * percentual_ganho / 100
        lbl_lucro_potencial.config(text=f"Lucro Potencial: R$ {lucro_potencial:.2f}")
    except ValueError:
        lbl_lucro_potencial.config(text="Lucro Potencial: -")
def atualizar_valores(event):
    codigo_ativo = entry_codigo_ativo.get()
    if codigo_ativo:
        if not validar_simbolo(codigo_ativo):
            lbl_resultado.config(text=f"Símbolo inválido: {codigo_ativo}.")
            return
        
        lote_info = consultar_lote(codigo_ativo)
        preco_ativo_usd = obter_preco_cripto(codigo_ativo)
        taxa_cambio = obter_taxa_cambio()
        preco_ativo_brl = preco_ativo_usd * taxa_cambio if preco_ativo_usd and taxa_cambio else None

        if lote_info and preco_ativo_usd and preco_ativo_brl:
            resultado_texto = (f"Preço atual de {codigo_ativo} (USD): ${preco_ativo_usd:.2f}\n"
                               f"Preço atual de {codigo_ativo} (R$): R$ {preco_ativo_brl:.2f}\n\n"
                               f"Tamanho mínimo do lote para {codigo_ativo}: {lote_info['minQty']}\n"
                               f"Tamanho máximo do lote para {codigo_ativo}: {lote_info['maxQty']}\n"
                               f"Incremento de tamanho do lote para {codigo_ativo}: {lote_info['stepSize']}")
            lbl_resultado.config(text=resultado_texto)
            entry_valor_atual_usd.delete(0, tk.END)
            entry_valor_atual_usd.insert(0, f"{preco_ativo_usd:.2f}")
            entry_valor_atual_brl.delete(0, tk.END)
            entry_valor_atual_brl.insert(0, f"{preco_ativo_brl:.2f}")
        else:
            lbl_resultado.config(text=f"Não foi possível obter informações de tamanho de lote para {codigo_ativo}.")
    else:
        lbl_resultado.config(text="Por favor, insira o código do ativo.")
import pandas as pd

def calcular_medias_moveis(codigo_ativo):
    # Obter dados de preços do ativo (últimos 40 períodos)
    candles = cliente_binance.get_klines(symbol=codigo_ativo, interval=Client.KLINE_INTERVAL_1DAY, limit=40)
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    
    # Calcular médias móveis
    df['close'] = df['close'].astype(float)
    df['media_rapida'] = df['close'].rolling(window=7).mean()
    df['media_lenta'] = df['close'].rolling(window=40).mean()
    
    media_rapida = df['media_rapida'].iloc[-1]
    media_lenta = df['media_lenta'].iloc[-1]
    
    return media_rapida, media_lenta
def abrir_ordem_oco(codigo_ativo, quantidade, preco_compra, percentual_ganho, percentual_perda):
    preco_alvo = preco_compra * (1 + percentual_ganho / 100)
    preco_stop = preco_compra * (1 - percentual_perda / 100)
    preco_stop_limit = preco_stop * 0.99  # 1% abaixo do preço stop
    
    try:
        order = cliente_binance.create_oco_order(
            symbol=codigo_ativo,
            side=Client.SIDE_SELL,
            quantity=quantidade,
            price=f"{preco_alvo:.2f}",
            stopPrice=f"{preco_stop:.2f}",
            stopLimitPrice=f"{preco_stop_limit:.2f}",
            stopLimitTimeInForce=Client.TIME_IN_FORCE_GTC
        )
        print(f"Ordem OCO aberta: {order}")
    except Exception as e:
        print(f"Erro ao abrir ordem OCO: {e}")


def enviar_informacoes():
    codigo_ativo = entry_codigo_ativo.get()
    valor_lote = entry_valor_lote.get()
    valor_atual_usd = entry_valor_atual_usd.get()
    valor_atual_brl = entry_valor_atual_brl.get()
    percentual_ganho = entry_percentual_ganho.get()
    percentual_perda = entry_percentual_perda.get()
    lucro_potencial = lbl_lucro_potencial.cget("text")

    # Garantir que os dados do lote sejam capturados corretamente
    lote_info = consultar_lote(codigo_ativo)
    if lote_info:
        # Obter data e hora atual
        now = datetime.datetime.now()
        data_hora = now.strftime("%Y-%m-%d %H:%M:%S")

        mensagem = (f"Data e Hora: {data_hora}\n"
                    f"Código do Ativo: {codigo_ativo}\n"
                    f"Valor do Lote: {valor_lote}\n"
                    f"Valor Atual (USD): {valor_atual_usd}\n"
                    f"Valor Atual (R$): {valor_atual_brl}\n"
                    f"Percentual de Ganho: {percentual_ganho}%\n"
                    f"Percentual de Perda: {percentual_perda}%\n"
                    f"{lucro_potencial}\n"
                    f"Tamanho mínimo do lote: {lote_info['minQty']}\n"
                    f"Tamanho máximo do lote: {lote_info['maxQty']}\n"
                    f"Incremento de tamanho do lote: {lote_info['stepSize']}")
        enviar_email_outlook(mensagem)
    else:
        lbl_resultado.config(text="Não foi possível obter informações de tamanho de lote para envio por e-mail.")
def verificar_e_comprar():
    codigo_ativo = entry_codigo_ativo.get()
    percentual_ganho = float(entry_percentual_ganho.get())
    percentual_perda = float(entry_percentual_perda.get())
    quantidade = float(entry_valor_lote.get())  # Supondo que o valor do lote seja a quantidade a comprar
    
    media_rapida, media_lenta = calcular_medias_moveis(codigo_ativo)
    
    if media_rapida > media_lenta:
        preco_compra = obter_preco_cripto(codigo_ativo)
        
        # Abrir ordem de compra
        try:
            order = cliente_binance.order_market_buy(
                symbol=codigo_ativo,
                quantity=quantidade
            )
            print(f"Ordem de compra aberta: {order}")
            
            # Após a compra, abrir ordem OCO
            abrir_ordem_oco(codigo_ativo, quantidade, preco_compra, percentual_ganho, percentual_perda)
            
        except Exception as e:
            print(f"Erro ao abrir ordem de compra: {e}")
    else:
        print("Condições de compra não atendidas (média rápida <= média lenta).")

root = tk.Tk()
root.title("Consulta de Tamanho de Lote e Lucro Potencial")

# Rótulo e campo de entrada para o código do ativo
tk.Label(root, text="Código do Ativo:").grid(row=0, column=0, padx=10, pady=10)
entry_codigo_ativo = tk.Entry(root)
entry_codigo_ativo.grid(row=0, column=1, padx=10, pady=10)
entry_codigo_ativo.bind("<KeyRelease>", atualizar_valores)

# Campo de entrada para o valor do lote
tk.Label(root, text="Valor do Lote:").grid(row=1, column=0, padx=10, pady=10)
entry_valor_lote = tk.Entry(root)
entry_valor_lote.grid(row=1, column=1, padx=10, pady=10)

# Campo de entrada para o valor atual (USD)
tk.Label(root, text="Valor Atual (USD):").grid(row=2, column=0, padx=10, pady=10)
entry_valor_atual_usd = tk.Entry(root)
entry_valor_atual_usd.grid(row=2, column=1, padx=10, pady=10)

# Campo de entrada para o valor atual (R$)
tk.Label(root, text="Valor Atual (R$):").grid(row=3, column=0, padx=10, pady=10)
entry_valor_atual_brl = tk.Entry(root)
entry_valor_atual_brl.grid(row=3, column=1, padx=10, pady=10)

# Campo de entrada para o percentual de ganho
tk.Label(root, text="Percentual de Ganho:").grid(row=4, column=0, padx=10, pady=10)
entry_percentual_ganho = tk.Entry(root)
entry_percentual_ganho.grid(row=4, column=1, padx=10, pady=10)
tk.Label(root, text="%").grid(row=4, column=2, padx=0, pady=10)
entry_percentual_ganho.bind("<KeyRelease>", calcular_lucro_potencial)

# Campo de entrada para o percentual de perda
tk.Label(root, text="Percentual de Perda:").grid(row=5, column=0, padx=10, pady=10)
entry_percentual_perda = tk.Entry(root)
entry_percentual_perda.grid(row=5, column=1, padx=10, pady=10)
tk.Label(root, text="%").grid(row=5, column=2, padx=0, pady=10)

# Rótulo para exibir lucro potencial
lbl_lucro_potencial = tk.Label(root, text="Lucro Potencial: -", justify=tk.LEFT)
lbl_lucro_potencial.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Botão para buscar as informações de lote
btn_buscar = tk.Button(root, text="Buscar Lote", command=buscar_lote)
btn_buscar.grid(row=7, columnspan=2, pady=10)
# Adicionar botão para verificar e comprar:
btn_verificar_comprar = tk.Button(root, text="Verificar e Comprar", command=verificar_e_comprar)
btn_verificar_comprar.grid(row=10, columnspan=2, pady=10)

# Botão para enviar informações por e-mail
btn_enviar = tk.Button(root, text="Enviar Informações", command=enviar_informacoes)
btn_enviar.grid(row=8, columnspan=2, pady=10)

# Rótulo para exibir o resultado
lbl_resultado = tk.Label(root, text="", justify=tk.LEFT)
lbl_resultado.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()

## FINAL DE PROGRAMA