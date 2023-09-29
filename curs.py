import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import io
import random
import xml.etree.ElementTree as ET

valutes_cb = {
'AED': 'R01230',
'AMD': 'R01060',
'AUD': 'R01010',
'AZN': 'R01020',
'BGN': 'R01100',
'BRL': 'R01115',
'BYN': 'R01090',
'CAD': 'R01350',
'CHF': 'R01775',
'CNY': 'R01375',
'CZK': 'R01760',
'DKK': 'R01215',
'EGP': 'R01240',
'EUR': 'R01239',
'GBP': 'R01035',
'GEL': 'R01210',
'HKD': 'R01200',
'HUF': 'R01135',
'IDR': 'R01280',
'INR': 'R01270',
'JPY': 'R01820',
'KGS': 'R01370',
'KRW': 'R01815',
'KZT': 'R01335',
'MDL': 'R01500',
'NOK': 'R01535',
'NZD': 'R01530',
'PLN': 'R01565',
'QAR': 'R01355',
'RON': 'R01585',
'RSD': 'R01804',
'SEK': 'R01770',
'SGD': 'R01625',
'THB': 'R01675',
'TJS': 'R01670',
'TMT': 'R01710',
'TRY': 'R01700',
'UAH': 'R01720',
'USD': 'R01235',
'UZS': 'R01717',
'VND': 'R01150',
'XDR': 'R01589',
'ZAR': 'R01810'
}

# Заголовки - без них не получается получить наборк курсов валют для построения графика
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}

    
# Получение списка курсов для кнопки Курс Основных в боте
def get_now_ruble_curses(valutes):
    result = {}
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    for valute in valutes:
        valute_name, valute_key = check_valute(valute)
        if valute_name and valute_key:
            curse = data['Valute'][valute]['Value']
            result[valute] = curse
    # print (result)
    return result    
    
# получение свежего курс адля 1 валюты
def get_now_ruble_curse(valute):
    valute_name, valute_key = check_valute(valute)
    if valute_name and valute_key:
        data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        curse = data['Valute'][valute]['Value']
        # print (valute)
        # print (curse)
        return curse
    else: return False


# проверка на то что боту передают число
def is_valid_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False
    

# получение курса одной валюты к другой (кроме рубля)
def get_now_other_curse(valute1, valute2):
    valute1_name, valute1_key = check_valute(valute1)
    valute2_name, valute2_key = check_valute(valute2)
    if valute1_name and valute2_name:
        data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        curse1 = data['Valute'][valute1]['Value']
        curse2 = data['Valute'][valute2]['Value']
        if curse1 and curse2:
            # print(float(curse1)/float(curse2))
            return float(curse1)/float(curse2)
        else:
            return False
    else: return False


# Проверка есть ли валюта в списке доступных
def check_valute(valute):
    if valute in valutes_cb.keys():
        return (valute, valutes_cb[valute])
    else:
        return (False, False)
    
def xml_to_csv(xml_string):
    # Создаем корневой элемент XML
    root = ET.fromstring(xml_string)

    # Инициализируем CSV-строку
    csv_data = ""

    # Перебираем элементы Record
    for record in root.findall('.//Record'):
        date = record.get('Date').replace(".", "")
        value = record.find('Value').text.replace(",", ".")
        csv_data += f"{root.get('ID')},{date},{value}\n"

    return csv_data
    
def get_graf(valute, period):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=period)

    formatted_end_date = end_date.strftime('%d/%m/%Y')
    formatted_start_date = start_date.strftime('%d/%m/%Y')
    valute_name, valute_key = check_valute(valute)
    try:
        if valute_name and valute_key:
            valute_name = valute_name+'CB'
            url = f'https://cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_start_date}&date_req2={formatted_end_date}&VAL_NM_RQ={valute_key}'
            response = requests.get(url, headers=headers)
            txt = xml_to_csv(response.text).split("\n")[:-1]
            x=[] #Здесь будут даты на горизонтальной оси.
            y=[] #Здесь будут цены на вертикальной оси.
            for line in txt: #цикл по прилетевшим значениям. Разносим их по x и y 
                tmp=line.split(",") #читаем строчку за строчкой и выбираем из неё данные (значения разделены запятой)
                date=tmp[1] #дата
                x.append(matplotlib.dates.date2num(datetime.strptime(date, '%d%m%Y'))) #запишем дату в понятном для библиотеки matplotlib виде (она станет числом)
                y.append(float(tmp[2])) #посчитаем типическую цену за день и добавим в chart_y. Типическая цена=(цена закрытия+максимум+минимум)/3. 
            fig, ax = plt.subplots() #начинаем работать с библиотекой matplotlib. Создаём фигуру.
            ymax = max(y) #находим максимальное значение, до которого доходил.
            xmax = x[y.index(ymax)] #находим дату максимального значения.
            ymax=round(ymax,2)#округляем максимум до копеек.
            print("Максимум был "+str(ymax))
            ax.annotate('MAX:'+str(ymax), #на график поместим аннотацию: максимальное значение доллара.
                        xy=(xmax, ymax*(1.005)), #место куда поместим аннотацию: визуально чуть-чуть повыше максимума. 
                        horizontalalignment='center', #выровняем метку максимума по центру.
                        )
            ax.plot(x, y, color="g") #наносим график доллара: оси x и y. Цвет зелёный.
            plt.title(valute_name, fontsize=20)
            if period > 700:
                ax.xaxis.set_major_locator(matplotlib.dates.YearLocator(1)) #делаем так, чтобы на оси дат были не числа типа 10.12.2018, а только годы
                ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y')) #формат оси x - годы.
            elif 200 < period <=400:
                ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=1))
                ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b')) #формат оси x - месяцы.
            elif 85 < period <=200:
                ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=1))
                ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %Y'))  #формат оси x - месяцы игоды.
            else:
                ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=4))
                ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d-%b'))  #формат оси x - дни и месяцы с шагом 4.
            plt.grid() #наносим сетку.
            # plt.show() #показываем график!
            buffer = io.BytesIO()
        
            # Сохраняем график в буфер
            plt.savefig(buffer, format='png')
            
            # Очищаем текущий график
            plt.clf()

            # Возвращаем буфер
            buffer.seek(0)
        else:
            with open('error.png', 'rb') as f:
                buffer = f.read()
        return buffer
    except:
        with open('error.png', 'rb') as f:
            buffer = f.read()
        return buffer
    
# get_graf('USD', 1)




# ВАРИАНТ С ГРАФИКАМИ ИЗ ФИНАМА (какие-то у них проблемы сейчас, так что переделал на Центробанк)



# valutes = {
#     'AED': 4043268,
#     'AMD': 498822,
#     'AUD': 498819,
#     'AZN': 498820,
#     'BGN': 498824,
#     'BRL': 498825,
#     'BYN': 498823,
#     'CAD': 498831,
#     'CHF': 498847,
#     'CNY': 498833,
#     'CZK': 498845,
#     'DKK': 498828,
#     'EGP': 4043269,
#     'EUR': 82486,
#     'GBP': 498821,
#     'GEL': 4043267,
#     'HKD': 498827,
#     'HUF': 498826,
#     'IDR': 4043270,
#     'INR': 498829,
#     'JPY': 498850,
#     'KGS': 498832,
#     'KRW': 498849,
#     'KZT': 498830,
#     'MDL': 498834,
#     'NOK': 498835,
#     'NZD': 4043272,
#     'PLN': 498836,
#     'QAR': 4043271,
#     'RON': 498837,
#     'RSD': 4043274,
#     'SEK': 498846,
#     'SGD': 498839,
#     'THB': 4043273,
#     'TJS': 498840,
#     'TMT': 498842,
#     'TRY': 498841,
#     'UAH': 498844,
#     'USD': 82485,
#     'UZS': 498843,
#     'VND': 4043266,
#     'XDR': 498838,
#     'ZAR': 498848
# }
# # Проверка есть ли валюта в списке доступных для финам
# def check_valute(valute):
#     if valute in valutes.keys():
#         return (valute, valutes[valute])
#     else:
#         return (False, False)

# # Построение графика при помощи финам
# def get_graf(valute, period):
#     end_date = datetime.today().date()
#     start_date = end_date - timedelta(days=period)

#     formatted_end_date = end_date.strftime('%d.%m.%Y')
#     formatted_start_date = start_date.strftime('%d.%m.%Y')
#     print(start_date)
#     graf_period=8
#     valute_name, valute_key = check_valute(valute)
#     if valute_name and valute_key:
#         valute_name = valute_name+'CB'
#         url = f'https://export.finam.ru/export9.out?check&market=41&em={str(valute_key)}&code={valute_name}&apply=0&df={start_date.day}&mf={start_date.month - 1}&yf={start_date.year}&from={formatted_start_date}&dt={end_date.day}&mt={end_date.month - 1}&yt={end_date.year}&to={formatted_end_date}&p=8&f={random.randint(100000, 99999999)}&e=.csv&cn={valute_name}&dtf=1&tmf=1&MSOR=1&mstime=on&mstimever=1&sep=1&sep2=1&datf=1'
#         print(url)
#         response = requests.get(url, headers=headers)
#         print(response.text)
#         txt = response.text.split("\r\n")[:-1]
#         x=[] #Здесь будут даты на горизонтальной оси.
#         y=[] #Здесь будут цены на вертикальной оси.
#         for line in txt: #цикл по прилетевшим значениям. Разносим их по x и y 
#             tmp=line.split(",") #читаем строчку за строчкой и выбираем из неё данные (значения разделены запятой)
#             date=tmp[2] #дата - это третье поле в строке
#             x.append(matplotlib.dates.date2num(datetime.strptime(date, '%Y%m%d'))) #запишем дату в понятном для библиотеки matplotlib виде (она станет числом)
#             y.append((float(tmp[5])+float(tmp[6])+float(tmp[7]))/3) #посчитаем типическую цену за день и добавим в chart_y. Типическая цена=(цена закрытия+максимум+минимум)/3. 
#         fig, ax = plt.subplots() #начинаем работать с библиотекой matplotlib. Создаём фигуру.
#         ymax = max(y) #находим максимальное значение, до которого доходил.
#         xmax = x[y.index(ymax)] #находим дату максимального значения.
#         ymax=round(ymax,2)#округляем максимум до копеек.
#         print("Максимум был "+str(ymax))
#         ax.annotate('MAX:'+str(ymax), #на график поместим аннотацию: максимальное значение доллара.
#                     xy=(xmax, ymax*(1.005)), #место куда поместим аннотацию: визуально чуть-чуть повыше максимума. 
#                     horizontalalignment='center', #выровняем метку максимума по центру.
#                     )
#         ax.plot(x, y, color="g") #наносим график доллара: оси x и y. Цвет зелёный.
#         plt.title(valute_name, fontsize=20)
#         if period > 700:
#             ax.xaxis.set_major_locator(matplotlib.dates.YearLocator(1)) #делаем так, чтобы на оси дат были не числа типа 10.12.2018, а только годы
#             ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y')) #формат оси x - годы.
#         elif 200 < period <=400:
#             ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=1))
#             ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b')) #формат оси x - месяцы.
#         elif 85 < period <=200:
#             ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=1))
#             ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %Y'))  #формат оси x - месяцы игоды.
#         else:
#             ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=4))
#             ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d-%b'))  #формат оси x - дни и месяцы с шагом 4.
#         plt.grid() #наносим сетку.
#         plt.show() #показываем график!
#         buffer = io.BytesIO()
    
#         # Сохраняем график в буфер
#         plt.savefig(buffer, format='png')
        
#         # Очищаем текущий график
#         plt.clf()

#         # Возвращаем буфер
#         buffer.seek(0)
#         return buffer