import os
import datetime
import pandas as pd
import seaborn as sns
import urllib.request
from spyre import server
import matplotlib.pyplot as plt


def download_data(region_id, start_year=1981, end_year=2024):
    if not os.path.exists("..\data_VHI"):
        os.makedirs("..\data_VHI")

    filename_pattern = f"VHI-ID_{region_id}_"
    existing_files = [file for file in os.listdir("..\data_VHI") if file.startswith(filename_pattern)]
    if existing_files:
        print(f"Файл для VHI-ID №{region_id} вже завантажено: {existing_files[0]}\n")
        return

    download_url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={region_id}&year1={start_year}&year2={end_year}&type=Mean"
    vhi_url_open = urllib.request.urlopen(download_url)

    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H-%M-%S")
    filename = f"VHI-ID_{region_id}_{current_date}_{current_time}.csv"

    file_path = os.path.join("..\data_VHI", filename)
    with open(file_path, 'wb') as output:
        output.write(vhi_url_open.read())

    print()
    print(f"VHI-файл {filename} успішно завантажено!")
    print(f"Файл збережено у: {os.path.abspath(file_path)}")
    print()

    return


def create_dataframesame(folder_path):
    frames, columns = [], ["Year", "Week", "SMN", "SMT", "VCI", "TCI", "VHI", "empty"]

    csv_files = filter(lambda x: x.endswith('.csv'), os.listdir(folder_path))

    for file_name in csv_files:
        file_path = os.path.join(folder_path, file_name)
        region_id = int(file_name.split('_')[1])

        df = pd.read_csv(file_path, header=1, names=columns)
        df.at[0, "Year"] = df.at[0, "Year"][9:]

        df = df.drop(df.index[-1])
        df = df.drop(df.loc[df["VHI"] == -1].index)
        df = df.drop("empty", axis=1)

        df.insert(0, "region_id", region_id, True)
        df['Year'] = df['Year'].astype(int)
        df['Week'] = df['Week'].astype(int)

        frames.append(df)

    df_result = pd.concat(frames).drop_duplicates().reset_index(drop=True)
    df_result = df_result.loc[(df_result.region_id != 12) & (df_result.region_id != 20)]

    return df_result


def update_region_id(df):
    region_mapping = {
        1: 22,
        2: 24,
        3: 23,
        4: 25,
        5: 3,
        6: 4,
        7: 8,
        8: 19,
        9: 20,
        10: 21,
        11: 9,
        13: 10,
        14: 11,
        15: 12,
        16: 13,
        17: 14,
        18: 15,
        19: 16,
        21: 17,
        22: 18,
        23: 6,
        24: 1,
        25: 2,
        26: 7,
        27: 5,
    }

    df_copy = df.copy()
    df_copy['region_id'] = df_copy['region_id'].replace(region_mapping)

    return df_copy


for index in range(1, 28):
    print(f"Завантаження CSV-файлу для VHI-ID №{index}...")
    download_data(index, 1981, 2024)

ids_with_names = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська',
    4: 'Донецька', 5: 'Житомирська', 6: 'Закарпатська',
    7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська',
    10: 'Кіровоградська', 11: 'Луганська', 12: 'Львівська',
    13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівненська', 17: 'Сумська', 18: 'Тернопільська',
    19: 'Харківська', 20: 'Херсонська', 21: 'Хмельницька',
    22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}


class WebAnalyzer(server.App):
    title = "lab3"

    inputs = [{
        "type": 'dropdown',
        "label": 'Виберіть дані',
        "options": [
            {"label": "Індекс стану рослинності (VCI)", "value": "VCI"},
            {"label": "Індекс температурного режиму (TCI)", "value": "TCI"},
            {"label": "Індекс здоров'я рослинності (VHI)", "value": "VHI"}
        ],
        "key": 'data_type',
        "action_id": "update_data"
    }, {
        "type": 'dropdown',
        "label": 'Виберіть область',
        "options": [{"label": f"{ids_with_names[region_id]}", "value": region_id}
                    for region_id in range(1, 26) if region_id not in [12, 20]],
        "key": 'region_id',
        "action_id": "update_data"
    }, {
        "type": 'text',
        "key": 'week_range',
        "label": 'Діапазон тижднів (1-52)',
        "value": '1-52',
        "action_id": 'update_data'
    }, {
        "type": 'dropdown',
        "label": 'Виберіть колір для карти',
        "options": [
            {"label": "Жовто-Зелено-Синя", "value": "YlGnBu"},
            {"label": "Червоно-Синя", "value": "RdBu"},
            {"label": "Фіолетово-Оранжева", "value": "PuOr"}
        ],
        "key": 'color_map',
        "action_id": 'update_data'
    }, {
        "type": 'text',
        "key": 'year_range',
        "label": 'Діапазон років',
        "value": 'Всі',
        "action_id": 'update_data'
    }, {
        "type": 'simple',
        "label": 'Submit',
        "key": 'submit_button',
        "id": 'update_data'
    }]

    controls = [{
        "type": "button",
        "label": "Оновити",
        "id": "update_data"
    }]

    tabs = ["Таблиця", "Карта"]

    outputs = [
        {
            "type": "table",
            "id": "table",
            "tab": "Таблиця",
            "control_id": "update_data"
        },
        {
            "type": "plot",
            "id": "plot",
            "tab": "Карта",
            "control_id": "update_data"
        }
    ]

    def getData(self, params):
        data_type = params['data_type']
        region_id = params.get('region_id', None)
        folder_path = "..\data_VHI"

        df_old = create_dataframesame(folder_path)
        df = update_region_id(df_old)

        week_range = params['week_range'].split('-')

        start_week = int(week_range[0])
        end_week = int(week_range[1])

        df = df[(df['Week'] >= start_week) & (df['Week'] <= end_week)]
        year_range = params['year_range']

        if year_range.lower() != 'всі':
            year_range = year_range.split('-')
            start_year = int(year_range[0])
            end_year = int(year_range[1])
            df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

        if region_id is not None:
            region_id = int(region_id)
            df = df[df['region_id'] == region_id]
        return df[['region_id', 'Year', 'Week', data_type]]

    def getPlot(self, params):
        df = self.getData(params)
        data_type = params['data_type']
        region_id = int(params['region_id'])
        region_name = ids_with_names[region_id]
        year_range = params['year_range']

        if year_range.lower() != 'всі':
            year_range = year_range.split('-')
            start_year = int(year_range[0])
            end_year = int(year_range[1])
            year_range = f"{start_year}-{end_year}"
        else:
            year_range = "Всі роки"

        plt.figure(figsize=(10, 15))
        plt.subplot(2, 1, 1)
        sns.heatmap(df.pivot(index='Year', columns='Week', values=data_type), cmap=params['color_map'],
                    cbar_kws={'label': data_type}, linewidths=.7)
        plt.title(f"Теплова карта {data_type} для області [{region_name}]\n{year_range}")
        plt.xlabel("Тиждень")
        plt.ylabel("Рік")
        plt.subplot(2, 1, 2)
        for year in df['Year'].unique():
            data_year = df[df['Year'] == year]
            plt.plot(data_year['Week'], data_year[data_type], marker='.', linestyle='-', label=year)

        plt.title(f'Графік {data_type} для області [{region_name}]\n{year_range}')
        plt.xlabel('Тиждень')
        plt.ylabel(data_type)
        plt.grid(True)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10), ncol=9)
        plt.tight_layout()
        return plt.gcf()

#ggsh
app = WebAnalyzer()
app.launch(port=4444)
