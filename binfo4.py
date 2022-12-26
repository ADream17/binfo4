import requests
import pandas as pd
import numpy as np
import plotly

from plotly.offline import download_plotlyjs, plot, iplot, init_notebook_mode
import plotly.graph_objs as go

# Sacar últimos 15000 datos de intervalos de 1 min

interval = "1m"

print(f'------------------------')
print(f'Downloading BTCUSDT data')
url = 'https://api.binance.com/api/v3/klines'
headers = {'accept': 'application/json'}
doc_columns = ['Open_Time', 'Open', 'High', 'Low', 'Close', 'Volumen', 'Close_Time', 'Quate_asset_vol',
               'Number_trades', 'Taker_buy_base', 'Taker_buy_quote', 'Ignore']

main_df = pd.DataFrame(columns=doc_columns)

pagination = True
initial_round = True
last_end_time = None
i = 0

while i < 15:
    if initial_round:
        print('Ronda inicial')
        body = {"symbol": 'BTCUSDT', "interval": interval, "limit": "1000"}
        initial_round = False
    else:
        body = {"symbol": 'BTCUSDT', "interval": interval,
                "limit": "1000", "endTime": end_time}

    response = requests.get(url, headers=headers, params=body)
    data = response.json()
    print('Data requested')

    df = pd.DataFrame(data, columns=doc_columns)
    df['Open_Timestamp'] = pd.to_datetime(df['Open_Time'], unit='ms')
    df['Close_Timestamp'] = pd.to_datetime(df['Close_Time'], unit='ms')

    main_df = pd.concat([main_df, df])
    main_df = main_df.sort_values(by='Open_Timestamp', ascending=True)
    end_time = str(main_df['Open_Time'].iloc[0])

    if last_end_time == end_time:
        print('Finishing fetching')
        break
    if i == 0:
        Precio = df.Open.rolling(1).mean()
    elif i > 0:
        Precio1 = df.Open.rolling(1).mean()
        Precio = [*Precio1, *Precio]

    last_end_time = end_time
    i = i+1

Precioso = pd.DataFrame(Precio, columns=['Open'])

# Cálculo de medias móviles simples


def sma(df, d):
    c = df.rolling(d).mean()
    return c.dropna()


price_columns = ['Open']
Price = pd.DataFrame(columns=price_columns)

Price['Open'] = sma(Precioso.Open, 1)
Price['sma5'] = sma(Precioso.Open, 5)
Price['sma10'] = sma(Precioso.Open, 10)
Price['sma25'] = sma(Precioso.Open, 25)
Price['sma75'] = sma(Precioso.Open, 75)
Price['sma150'] = sma(Precioso.Open, 150)
Price['sma375'] = sma(Precioso.Open, 375)
Price['sma500'] = sma(Precioso.Open, 500)
Price['sma1500'] = sma(Precioso.Open, 1500)

Derivada = pd.DataFrame(columns=['d5', 'd10', 'd25', 'd75', 'd150', 'd375', 'd500', 'd1500'],
                        index=range(15000))
Derivada2 = pd.DataFrame(columns=['t150', 't375', 't500', 't1500', 'r150', 'r375',
                                  'r500', 'r1500', 'x100'],
                         index=range(15000))

# por ahora sólo graficaremos
######## Estrategia de trading, prueba con --= y ++#
Indicador = 1
Dinerito = 1
Price['Compra'] = np.nan
Price['Venta'] = np.nan
CompraAnterior = 0
VentaAnterior = 0
I = 0

i = 1500
while i < 15000:
    Derivada['d5'][i] = Price['sma5'][i]-Price['sma5'][i-1]
    Derivada['d10'][i] = Price['sma10'][i]-Price['sma10'][i-1]
    Derivada['d25'][i] = Price['sma25'][i]-Price['sma25'][i-1]
    Derivada['d75'][i] = Price['sma75'][i]-Price['sma75'][i-1]
    Derivada['d150'][i] = Price['sma150'][i]-Price['sma150'][i-1]
    Derivada['d375'][i] = Price['sma375'][i]-Price['sma375'][i-1]
    Derivada['d500'][i] = Price['sma500'][i]-Price['sma500'][i-1]
    Derivada['d1500'][i] = Price['sma1500'][i]-Price['sma1500'][i-1]

    Derivada2['r150'][i] = (
        Price['Open'][i]-Price['sma150'][i])/Price['sma150'][i]
    Derivada2['r375'][i] = (
        Price['Open'][i]-Price['sma375'][i])/Price['sma375'][i]
    Derivada2['r500'][i] = (
        Price['Open'][i]-Price['sma500'][i])/Price['sma500'][i]
    Derivada2['r1500'][i] = (
        Price['Open'][i]-Price['sma1500'][i])/Price['sma1500'][i]

    if (Derivada['d5'][i] > 0 and Derivada['d10'][i] > 0 and Derivada['d25'][i] > 0 and
        Derivada['d75'][i] > 0 and Derivada['d150'][i] > 0 and Derivada['d375'][i] > 0 and
            Derivada['d500'][i] > 0 and Derivada['d1500'][i] > 0):
        Derivada2['x100'][i] = 5*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] < 0 and Derivada['d10'][i] < 0 and Derivada['d25'][i] < 0 and
          Derivada['d75'][i] < 0 and Derivada['d150'][i] < 0 and Derivada['d375'][i] < 0 and
          Derivada['d500'][i] < 0 and Derivada['d1500'][i] < 0):
        Derivada2['x100'][i] = -5*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] > 0 and Derivada['d10'][i] > 0 and Derivada['d25'][i] > 0 and
          Derivada['d75'][i] > 0 and Derivada['d150'][i] > 0 and Derivada['d375'][i] > 0 and
          Derivada['d500'][i] > 0):
        Derivada2['x100'][i] = 4.9*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] < 0 and Derivada['d10'][i] < 0 and Derivada['d25'][i] < 0 and
          Derivada['d75'][i] < 0 and Derivada['d150'][i] < 0 and Derivada['d375'][i] < 0 and
          Derivada['d500'][i] < 0):
        Derivada2['x100'][i] = -4.9*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] > 0 and Derivada['d10'][i] > 0 and Derivada['d25'][i] > 0 and
          Derivada['d75'][i] > 0 and Derivada['d150'][i] > 0 and Derivada['d375'][i] > 0):
        Derivada2['x100'][i] = 4.8*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] < 0 and Derivada['d10'][i] < 0 and Derivada['d25'][i] < 0 and
          Derivada['d75'][i] < 0 and Derivada['d150'][i] < 0 and Derivada['d375'][i] < 0):
        Derivada2['x100'][i] = -4.8*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] > 0 and Derivada['d10'][i] > 0 and Derivada['d25'][i] > 0 and
          Derivada['d75'][i] > 0 and Derivada['d150'][i] > 0):
        Derivada2['x100'][i] = 4.7*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] < 0 and Derivada['d10'][i] < 0 and Derivada['d25'][i] < 0 and
          Derivada['d75'][i] < 0 and Derivada['d150'][i] < 0):
        Derivada2['x100'][i] = -4.7*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] > 0 and Derivada['d10'][i] > 0 and Derivada['d25'][i] > 0 and
          Derivada['d75'][i] > 0):
        Derivada2['x100'][i] = 4.6*Price['Open'][i]/Price['Open'][i]
    elif (Derivada['d5'][i] < 0 and Derivada['d10'][i] < 0 and Derivada['d25'][i] < 0 and
          Derivada['d75'][i] < 0):
        Derivada2['x100'][i] = -4.6*Price['Open'][i]/Price['Open'][i]

    # Implementacion estrategia derivada de SMA1500
    if abs(Derivada['d1500'][i]) < 0.3:
        Derivada['d1500'][i] = 0

    # Implementacion estrategia derivada de cruce de SMA rapidas
    if abs(Derivada['d5'][i]) < 12:
        Derivada['d5'][i] = 0
    if abs(Derivada['d10'][i]) < 7:
        Derivada['d10'][i] = 0
    if abs(Derivada['d25'][i]) < 3:
        Derivada['d25'][i] = 0


# Proximamente el algoritmo de compra venta
    i = i+1

Derivada2['t150'] = sma(Derivada.d150, 1)
Derivada2['t150'] = Derivada2['t150'].apply(np.sign)
Derivada2['t375'] = sma(Derivada.d375, 1)
Derivada2['t375'] = 2*Derivada2['t375'].apply(np.sign)
Derivada2['t500'] = sma(Derivada.d500, 1)
Derivada2['t500'] = 3*Derivada2['t500'].apply(np.sign)
Derivada2['t1500'] = sma(Derivada.d1500, 1)
Derivada2['t1500'] = 4*Derivada2['t1500'].apply(np.sign)


# if -a*-b*-c>0 or -a*-d>0 or -b*-d>0:

columnas = ['Open', 'sma5', 'sma10', 'sma25', 'sma75', 'sma150', 'sma375', 'sma500',
            'sma1500', 'Compra', 'Venta']
#columnas2 = ['d5','d10','d25','d75','d150','d375','d500','d1500']
#########
fig = go.Figure()
for columna in columnas:
    if columna == 'Compra':
        fig.add_trace(go.Scatter(x=Price.index, y=Price[columna],
                                 mode='markers',
                                 name=columna,
                                 marker=dict(color='yellow')
                                 ))
    elif columna == 'Venta':
        fig.add_trace(go.Scatter(x=Price.index, y=Price[columna],
                                 mode='markers',
                                 name=columna,
                                 marker=dict(color='white')
                                 ))
    else:
        fig.add_trace(go.Scatter(x=Price.index, y=Price[columna],
                                 mode='lines',
                                 name=columna))
fig.update_layout(template='plotly_dark')
iplot(fig)
###################
columnas2 = ['d5', 'd10', 'd25']

fig = go.Figure()
for columna in columnas2:
    fig.add_trace(go.Scatter(x=Derivada.index, y=Derivada[columna],
                             mode='lines',
                             name=columna))
fig.update_layout(template='plotly_dark')
iplot(fig)
########
Derivada2['r1500'] = 100*Derivada2['r1500']
Derivada2['d10'] = Derivada['d10']/25
columnas3 = ['t150', 't1500', 'x100', 'r1500', 'd10']

fig = go.Figure()
for columna in columnas3:
    fig.add_trace(go.Scatter(x=Derivada2.index, y=Derivada2[columna],
                             mode='lines',
                             name=columna))
fig.update_layout(template='plotly_dark')
iplot(fig)

#########
#columnas4 = ['r150','r375','r500','r1500']
#
#fig = go.Figure()
# for columna in columnas4:
#    fig.add_trace(go.Scatter(x=Derivada2.index, y=Derivada2[columna],
#                                mode='lines',
#                                name=columna))
# fig.update_layout(template='plotly_dark')
# iplot(fig)
