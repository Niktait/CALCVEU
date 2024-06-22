import tkinter as tk
from tkinter import messagebox
import math
import sqlite3
from datetime import datetime
import pickle
import tkinter.ttk as ttk

# Функция для расчета мощности ветрогенератора.
# Принимает на вход скорость ветра (в м/с), радиус ротора (в метрах),
# коэффициенты КПД генератора и редуктора.
# Возвращает прогнозируемую мощность ветрогенератора (в ваттах).
def wind_power(speed, rotor_radius, generator_efficiency, gearbox_efficiency):
    # Плотность воздуха (кг/м³)
    density = 1.2041  
    # Коэффициент мощности (КПД) ветроэнергетической установки
    cp = 0.593  
    # Площадь поперечного сечения ротора (м²)
    area = math.pi * rotor_radius ** 2  
    # Расчет мощности ветрогенератора по формуле
    power = 0.5 * area * density * speed ** 3 * cp * generator_efficiency * gearbox_efficiency
    return power


# Функция для расчета энергии
def calculate_energy(power):
    hours_in_day = 24
    days_in_month = 30
    months_in_year = 12
    energy_per_day = power / 1000 * hours_in_day
    energy_per_month = energy_per_day * days_in_month
    energy_per_year = energy_per_month * months_in_year
    return energy_per_day, energy_per_month, energy_per_year

# Функция для сохранения в базу данных SQLite
def save_to_database(speed, radius, generator_efficiency, gearbox_efficiency, power, date_time):
    conn = sqlite3.connect('wind_power_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS wind_power_results
                 (speed REAL, radius REAL, generator_efficiency REAL,
                 gearbox_efficiency REAL, power REAL, date_time TEXT)''')
    c.execute("INSERT INTO wind_power_results VALUES (?, ?, ?, ?, ?, ?)",
              (speed, radius, generator_efficiency, gearbox_efficiency, power, date_time))
    conn.commit()
    conn.close()










# Функция для отображения окна с результатами
def show_results(power, energy_per_day, energy_per_month, energy_per_year):
    result_window = tk.Toplevel(root)
    result_window.title("Результаты расчета")
    result_window.geometry("400x300")

    result_label = tk.Label(result_window, text="Ожидаемая мощность генератора: {:.2f} ватт\n"
                                                 "Прогнозируемое получение энергии:\n"
                                                 "- {:.2f} кВт в сутки\n"
                                                 "- {:.2f} кВт в месяц\n"
                                                 "- {:.2f} кВт в год".format(power, energy_per_day, energy_per_month, energy_per_year),
                             font=("Arial", 12))
    result_label.pack(padx=10, pady=10)

    save_button = tk.Button(result_window, text="Сохранить в базу данных", command=lambda: save_to_database(
        float(speed_entry.get()), float(radius_entry.get()), float(generator_eff_entry.get()),
        float(gearbox_eff_entry.get()), power, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    save_button.pack(pady=5)

    show_database_button = tk.Button(result_window, text="Просмотреть базу данных", command=show_database)
    show_database_button.pack(pady=5)


def show_database():
    conn = sqlite3.connect('wind_power_results.db')
    c = conn.cursor()
    c.execute("SELECT * FROM wind_power_results")
    rows = c.fetchall()
    conn.close()

    # Отображение результатов из базы данных
    result_window = tk.Toplevel(root)
    result_window.title("Результаты из базы данных")
    result_window.geometry("1500x400")

    tree = ttk.Treeview(result_window)
    tree["columns"] = ("speed", "radius", "generator_efficiency", "gearbox_efficiency", "power", "date_time")
    tree.heading("speed", text="Скорость")
    tree.heading("radius", text="Радиус")
    tree.heading("generator_efficiency", text="КПД генератора")
    tree.heading("gearbox_efficiency", text="КПД редуктора")
    tree.heading("power", text="Мощность")
    tree.heading("date_time", text="Дата и время")
    
    for row in rows:
        formatted_datetime = datetime.fromisoformat(row[5]).strftime("%Y-%m-%d %H:%M:%S")
        tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], formatted_datetime))

    tree.pack(expand=True, fill="both")



























def calculate_power():
    try:
        # Получение значений из полей ввода и их преобразование в числа
        speed = float(speed_entry.get())
        rotor_radius = float(radius_entry.get())
        generator_efficiency = float(generator_eff_entry.get())
        gearbox_efficiency = float(gearbox_eff_entry.get())

        # Проверка соответствия значений диапазонам
        if not (5 <= rotor_radius <= 100):
            raise ValueError("Радиус ротора должен быть в диапазоне от 5 до 100 м")

        if not (0.75 <= generator_efficiency <= 0.95):
            raise ValueError("КПД генератора должен быть в диапазоне от 0.75 до 0.95")

        if not (0 <= speed <= 30):
            raise ValueError("Скорость ветра должна быть в диапазоне от 0 до 30 м/с")

        if not (0.85 <= gearbox_efficiency <= 0.98):
            raise ValueError("КПД редуктора должен быть в диапазоне от 0.85 до 0.98")

        # Расчет мощности ветрогенератора и соответствующей энергии
        power = wind_power(speed, rotor_radius, generator_efficiency, gearbox_efficiency)
        energy_per_day, energy_per_month, energy_per_year = calculate_energy(power)

        # Отображение результатов расчетов
        show_results(power, energy_per_day, energy_per_month, energy_per_year)

        # Сохранение введенных значений в файл
        save_values(speed, rotor_radius, generator_efficiency, gearbox_efficiency)

    except ValueError as e:
        # В случае некорректного ввода отображается сообщение об ошибке
        messagebox.showerror("Ошибка", str(e))




# Функция для сохранения введенных данных
def save_values(speed, radius, generator_efficiency, gearbox_efficiency):
    # Сохраняем значения в файл
    with open("values.pkl", "wb") as f:
        pickle.dump((speed, radius, generator_efficiency, gearbox_efficiency), f)

# Функция для загрузки последних введенных данных
def load_values():
    try:
        # Загружаем значения из файла
        with open("values.pkl", "rb") as f:
            speed, radius, generator_efficiency, gearbox_efficiency = pickle.load(f)
        # Вставляем загруженные значения в соответствующие поля
        speed_entry.insert(0, speed)
        radius_entry.insert(0, radius)
        generator_eff_entry.insert(0, generator_efficiency)
        gearbox_eff_entry.insert(0, gearbox_efficiency)
    except FileNotFoundError:
        pass  # Файл с сохраненными значениями не найден, игнорируем это

# Создаем окно программы
root = tk.Tk()
root.title("Калькулятор ветрогенератора")
root.geometry("550x650")

# Создаем фрейм для компоновки элементов управления
frame = tk.Frame(root)
frame.pack(expand=True, padx=10, pady=10)

# Создаем и размещаем элементы управления
speed_label = tk.Label(frame, text="Скорость ветра (м/с):", font=("Arial", 12))
speed_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
speed_entry = tk.Entry(frame, width=10, font=("Arial", 12))
speed_entry.grid(row=0, column=1, padx=10, pady=10)

# Добавляем описание диапазона для скорости ветра
speed_range_label = tk.Label(frame, text="от 0 до 30 м/с", font=("Arial", 10))
speed_range_label.grid(row=0, column=2, sticky="w", padx=5, pady=10)

radius_label = tk.Label(frame, text="Радиус ротора (м):", font=("Arial", 12))
radius_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
radius_entry = tk.Entry(frame, width=10, font=("Arial", 12))
radius_entry.grid(row=1, column=1, padx=10, pady=10)

# Добавляем описание диапазона для радиуса ротора
radius_range_label = tk.Label(frame, text="от 5 до 100 м", font=("Arial", 10))
radius_range_label.grid(row=1, column=2, sticky="w", padx=5, pady=10)

generator_eff_label = tk.Label(frame, text="КПД генератора:", font=("Arial", 12))
generator_eff_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)
generator_eff_entry = tk.Entry(frame, width=10, font=("Arial", 12))
generator_eff_entry.grid(row=2, column=1, padx=10, pady=10)

# Добавляем описание диапазона для коэффициента КПД генератора
generator_eff_range_label = tk.Label(frame, text="от 0.75 до 0.95", font=("Arial", 10))
generator_eff_range_label.grid(row=2, column=2, sticky="w", padx=5, pady=10)

gearbox_eff_label = tk.Label(frame, text="КПД редуктора:", font=("Arial", 12))
gearbox_eff_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)
gearbox_eff_entry = tk.Entry(frame, width=10, font=("Arial", 12))
gearbox_eff_entry.grid(row=3, column=1, padx=10, pady=10)

# Добавляем описание диапазона для коэффициента КПД редуктора
gearbox_eff_range_label = tk.Label(frame, text="от 0.85 до 0.98", font=("Arial", 10))
gearbox_eff_range_label.grid(row=3, column=2, sticky="w", padx=5, pady=10)

calculate_button = tk.Button(frame, text="Рассчитать", command=calculate_power, font=("Arial", 14))
calculate_button.grid(row=10, columnspan=10, pady=30)





def calculate_nominal_power(rotor_radius, generator_efficiency, wind_speed):
    # Параметры для расчета номинальной мощности
    density = 1.225  # Плотность воздуха в кг/м^3 (значение для стандартных атмосферных условий)
    cp = 0.35  # Коэффициент мощности ветроэнергетической установки (может меняться в зависимости от типа и модели)
    
    # Вычисление площади поперечного сечения ротора
    rotor_area = math.pi * (rotor_radius ** 2)
    
    # Вычисление номинальной мощности
    nominal_power = 0.5 * density * cp * rotor_area * (wind_speed ** 3) * generator_efficiency
    
    return nominal_power


def open_nominal_power_window():
    # Создание нового окна для ввода данных
    nominal_power_window = tk.Toplevel(root)
    nominal_power_window.title("Определение номинальной мощности ВЭУ")
    nominal_power_window.geometry("300x300")

    # Создание меток и полей ввода для параметров
    rotor_radius_label = tk.Label(nominal_power_window, text="Радиус ротора (м):", font=("Arial", 12))
    rotor_radius_label.grid(row=0, column=0, padx=10, pady=10)
    rotor_radius_entry = tk.Entry(nominal_power_window, width=10, font=("Arial", 12))
    rotor_radius_entry.grid(row=0, column=1, padx=10, pady=10)

    generator_efficiency_label = tk.Label(nominal_power_window, text="КПД генератора:", font=("Arial", 12))
    generator_efficiency_label.grid(row=1, column=0, padx=10, pady=10)
    generator_efficiency_entry = tk.Entry(nominal_power_window, width=10, font=("Arial", 12))
    generator_efficiency_entry.grid(row=1, column=1, padx=10, pady=10)

    wind_speed_label = tk.Label(nominal_power_window, text="Скорость ветра (м/с):", font=("Arial", 12))
    wind_speed_label.grid(row=2, column=0, padx=10, pady=10)
    wind_speed_entry = tk.Entry(nominal_power_window, width=10, font=("Arial", 12))
    wind_speed_entry.grid(row=2, column=1, padx=10, pady=10)

    # Создание функции для вычисления номинальной мощности при нажатии на кнопку
    def calculate_nominal_power_from_window():
        try:
            # Получение значений из полей ввода
            rotor_radius = float(rotor_radius_entry.get())
            generator_efficiency = float(generator_efficiency_entry.get())
            wind_speed = float(wind_speed_entry.get())

            # Вычисление номинальной мощности
            nominal_power = calculate_nominal_power(rotor_radius, generator_efficiency, wind_speed)

            # Отображение результата в новом окне
            result_label = tk.Label(nominal_power_window, text=f"Номинальная мощность: {nominal_power:.2f} Вт", font=("Arial", 12))
            result_label.grid(row=3, columnspan=2, padx=10, pady=10)

        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения.")

    # Создание кнопки для запуска расчета номинальной мощности
    calculate_button = tk.Button(nominal_power_window, text="Рассчитать", command=calculate_nominal_power_from_window, font=("Arial", 12))
    calculate_button.grid(row=4, columnspan=2, pady=10)

# Создание кнопки "Определение номинальной мощности ВЭУ"
nominal_power_button = tk.Button(frame, text="Определение номинальной мощности ВЭУ", command=open_nominal_power_window, font=("Arial", 14))
nominal_power_button.grid(row=20, columnspan=10, pady=30)








def open_calculation_window():
    # Создаем новое окно для ввода данных
    calculation_window = tk.Toplevel(root)
    calculation_window.title("Расчет площади ВЭУ")
    calculation_window.geometry("400x200")

    
    # Создаем и размещаем поля ввода в новом окне
    diameter_label = tk.Label(calculation_window, text="Диаметр трубы мачты (м):")
    diameter_label.grid(row=0, column=0, padx=10, pady=5)
    diameter_entry = tk.Entry(calculation_window)
    diameter_entry.grid(row=0, column=1, padx=10, pady=5)

    height_label = tk.Label(calculation_window, text="Высота мачты (м):")
    height_label.grid(row=1, column=0, padx=10, pady=5)
    height_entry = tk.Entry(calculation_window)
    height_entry.grid(row=1, column=1, padx=10, pady=5)

    angle_label = tk.Label(calculation_window, text="Угол натяжения растяжек (градусы):")
    angle_label.grid(row=2, column=0, padx=10, pady=5)
    angle_entry = tk.Entry(calculation_window)
    angle_entry.grid(row=2, column=1, padx=10, pady=5)

    # Создаем кнопку для выполнения расчета
    calculate_button = tk.Button(calculation_window, text="Рассчитать", command=lambda: calculate_area_of_ground_surface(diameter_entry, height_entry, angle_entry), font=("Arial", 14))
    calculate_button.grid(row=3, columnspan=2, pady=10)

def calculate_area_of_ground_surface(diameter_entry, height_entry, angle_entry):
    try:
        # Получение значений из полей ввода и их преобразование в числа
        d = float(diameter_entry.get())
        h = float(height_entry.get())
        omega = float(angle_entry.get())

        # Проверка соответствия значений диапазонам
        if not (5 <= d <= 100):
            raise ValueError("Диаметр трубы мачты должен быть в диапазоне от 5 до 100 м")

        if not (0 <= h <= 200):
            raise ValueError("Высота мачты должна быть в диапазоне от 0 до 200 м")

        if not (0 <= omega <= 90):
            raise ValueError("Угол натяжения растяжек должен быть в диапазоне от 0 до 90 градусов")

        # Расчет площади занимаемой ВЭУ
        S_m = math.pi * d ** 2 / 4
        D_r = 2 * h * math.sin(math.radians(omega))
        S_r = math.pi * D_r ** 2 / 4
        total_area = S_m + S_r

        # Отображение результата
        result_text = "Площадь занимаемой ВЭУ: {:.2f} кв.м".format(total_area)
        messagebox.showinfo("Результат", result_text)

    except ValueError as e:
        # В случае некорректного ввода отображается сообщение об ошибке
        messagebox.showerror("Ошибка", str(e))




calculate_button = tk.Button(frame, text="Определение площади ВЭУ", command=open_calculation_window, font=("Arial", 14))
calculate_button.grid(row=30, columnspan=10, pady=30)




def open_combined_tasks_window():
    combined_tasks_window = tk.Toplevel(root)
    combined_tasks_window.title("Комбинированные задачи")
    combined_tasks_window.geometry("500x400")

    # Создание кнопок для задач
    task1_button = tk.Button(combined_tasks_window, text="Расчет параметров компонентов ВЭУ", width=30,command=open_wind_turbine_parameters_window)
    task1_button.pack(pady=(10, 5))  # Расположение с отступом сверху и снизу

    subtasks_frame = tk.Frame(combined_tasks_window)
    subtasks_frame.pack(pady=5)

    task2_1_button = tk.Button(subtasks_frame, text="Расчет ВЭУ", width=15, command=open_wind_turbine_parameters_window)
    task2_1_button.grid(row=0, column=0, padx=(0, 5), pady=5)

    # Создание кнопки для запуска окна ввода параметров
    solar_panel_button = tk.Button(subtasks_frame, text="Расчет СБ", width=15, command=open_solar_panel_parameters_window)
    solar_panel_button.grid(row=0, column=1, padx=(5, 0), pady=5)  # Расположение в сетке с отступом слева

    # Создание кнопки для запуска расчета
    geu_button = tk.Button(subtasks_frame, text="Расчет ГЭУ", width=15, command=calculate_geu_output)
    geu_button.grid(row=1, column=0, padx=(0, 5), pady=5)

    # Создание кнопки для открытия окна срока окупаемости оборудования
    payback_button = tk.Button(subtasks_frame, text="Срок окупаемости оборудования", width=30, command=open_payback_period_window)
    payback_button.grid(row=1, column=1, padx=(5, 0), pady=5)

    task2_5_button = tk.Button(combined_tasks_window, text="Аккумуляторные батареи", width=30, command=open_battery_parameters_window)
    task2_5_button.pack(pady=5)


# Создание кнопки для открытия окна "Комбинированные задачи"
combined_tasks_button = tk.Button(root, text="Комбинированные задачи", command=open_combined_tasks_window, font=("Arial", 14))
combined_tasks_button.pack(pady=20)




def open_battery_parameters_window():
    # Создание нового окна для ввода параметров
    battery_window = tk.Toplevel()
    battery_window.title("Параметры аккумуляторных батарей")
    battery_window.geometry("600x200")

    # Создание и размещение элементов управления для ввода параметров
    capacity_label = tk.Label(battery_window, text="Емкость батареи (А·ч):")
    capacity_label.grid(row=0, column=0, padx=10, pady=5)
    capacity_entry = tk.Entry(battery_window)
    capacity_entry.grid(row=0, column=1, padx=10, pady=5)

    quantity_label = tk.Label(battery_window, text="Количество батарей:")
    quantity_label.grid(row=1, column=0, padx=10, pady=5)
    quantity_entry = tk.Entry(battery_window)
    quantity_entry.grid(row=1, column=1, padx=10, pady=5)

    hours_label = tk.Label(battery_window, text="Время гарантированного энергоснабжения (часы):")
    hours_label.grid(row=2, column=0, padx=10, pady=5)
    hours_entry = tk.Entry(battery_window)
    hours_entry.grid(row=2, column=1, padx=10, pady=5)

    # Создание кнопки для запуска расчета
    calculate_button = tk.Button(battery_window, text="Рассчитать", command=lambda: calculate_battery_cost(battery_window, capacity_entry.get(), quantity_entry.get(), hours_entry.get()))
    calculate_button.grid(row=3, columnspan=2, pady=10)

    # Фокусируемся на первом поле ввода
    capacity_entry.focus_set()

def calculate_battery_cost(window, capacity, quantity, hours):
    try:
        # Преобразование входных данных в числа
        capacity = float(capacity)
        quantity = int(quantity)
        hours = int(hours)

        # Расчет стоимости батарей
        battery_cost_per_unit = 2000  # Стоимость одной аккумуляторной батареи
        total_cost = quantity * battery_cost_per_unit

        # Отображение результата
        result_text = f"Стоимость аккумуляторных батарей: {total_cost} руб."
        messagebox.showinfo("Результат", result_text)

        # Закрытие окна после отображения результата
        window.destroy()

    except Exception as e:
        # Обработка исключений, если что-то пошло не так
        messagebox.showerror("Ошибка", str(e))


def open_payback_period_window():
    # Создание нового окна для отображения срока окупаемости оборудования
    payback_window = tk.Toplevel()
    payback_window.title("Срок окупаемости оборудования")
    payback_window.geometry("300x200")

    # Расчет срока окупаемости для разных типов оборудования
    veu_payback_period = 14  # Срок окупаемости для ВЭУ-3 (в месяцах)
    sb_payback_period = 9    # Срок окупаемости для СБ-3 (в месяцах)
    geu_payback_period = 11  # Срок окупаемости для ГЭУ-6 (в месяцах)

    # Отображение результата
    result_text = f"Срок окупаемости для ВЭУ-3: {veu_payback_period} месяцев\n"
    result_text += f"Срок окупаемости для СБ-3: {sb_payback_period} месяцев\n"
    result_text += f"Срок окупаемости для ГЭУ-6: {geu_payback_period} месяцев"
    label = tk.Label(payback_window, text=result_text)
    label.pack(pady=20)







def calculate_geu_output():
    def open_geu_parameters_window():
        geu_params_window = tk.Toplevel()
        geu_params_window.title("Параметры ГЭУ")
        
        veu_power_label = tk.Label(geu_params_window, text="Мощность ВЭУ (кВт):")
        veu_power_label.grid(row=0, column=0, padx=10, pady=5)
        veu_power_entry = tk.Entry(geu_params_window)
        veu_power_entry.grid(row=0, column=1, padx=10, pady=5)

        sb_power_label = tk.Label(geu_params_window, text="Мощность СБ (кВт):")
        sb_power_label.grid(row=1, column=0, padx=10, pady=5)
        sb_power_entry = tk.Entry(geu_params_window)
        sb_power_entry.grid(row=1, column=1, padx=10, pady=5)

        veu_price_label = tk.Label(geu_params_window, text="Цена ВЭУ (руб.):")
        veu_price_label.grid(row=2, column=0, padx=10, pady=5)
        veu_price_entry = tk.Entry(geu_params_window)
        veu_price_entry.grid(row=2, column=1, padx=10, pady=5)

        sb_price_label = tk.Label(geu_params_window, text="Цена СБ (руб.):")
        sb_price_label.grid(row=3, column=0, padx=10, pady=5)
        sb_price_entry = tk.Entry(geu_params_window)
        sb_price_entry.grid(row=3, column=1, padx=10, pady=5)

        calculate_button = tk.Button(geu_params_window, text="Рассчитать", command=lambda: calculate_geu_output_internal(veu_power_entry.get(), sb_power_entry.get(), veu_price_entry.get(), sb_price_entry.get()))
        calculate_button.grid(row=4, columnspan=2, pady=10)

    def calculate_geu_output_internal(veu_power, sb_power, veu_price, sb_price):
        try:
            veu_power = float(veu_power)
            sb_power = float(sb_power)
            veu_price = float(veu_price)
            sb_price = float(sb_price)
            
            geu_power = veu_power + sb_power  # Общая мощность ГЭУ, кВт
            service_life = 20   # Срок службы оборудования, лет
            repair_cost_per_year = 3000  # Расходы на ремонт в год, руб.
            geu_amortization_per_hour = 1.83  # Амортизация ГЭУ в час, руб.
            average_wind_speed = 5.0  # Средняя скорость ветра в регионе (м/с)
            average_illumination = 700  # Средняя освещенность в регионе (Вт/м^2)
            veu_power_at_avg_wind_speed = 0.400  # Мощность ВЭУ на средней скорости ветра, кВт
            sb_power_at_avg_illumination = 2.1  # Мощность СБ на средней освещенности, кВт

            # Расчет выработки электроэнергии ГЭУ
            veu_output = veu_power_at_avg_wind_speed * veu_power  # Выработка энергии ВЭУ при средней скорости ветра, кВт*ч
            sb_output = sb_power_at_avg_illumination * sb_power      # Выработка энергии СБ при средней освещенности, кВт*ч
            geu_output = veu_output + sb_output                      # Общая выработка ГЭУ, кВт*ч
           
            # Отображение результата
            result_text = f"Выработка электроэнергии ГЭУ: {geu_output:.2f} кВт*ч"
            messagebox.showinfo("Результат", result_text)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # Открываем окно для ввода параметров
    open_geu_parameters_window()



    
def calculate_solar_panel_output(modules, nominal_power_per_module, radiation_per_day):
    try:
        modules = int(modules)
        nominal_power_per_module = float(nominal_power_per_module)
        radiation_per_day = float(radiation_per_day)

        daily_output_per_module = radiation_per_day * 1.27  # Дневная выработка одного модуля, кВт·ч/день
        yearly_output_per_module = daily_output_per_module * 365  # Годовая выработка одного модуля, кВт·ч
        total_yearly_output = yearly_output_per_module * modules  # Годовая выработка всей солнечной батареи, кВт·ч

        result_text = f"Годовая выработка солнечной батареи: {total_yearly_output} кВт·ч\n"
        result_text += f"Дневная выработка одного модуля: {daily_output_per_module:.2f} кВт·ч/день\n"
        result_text += f"Годовая выработка одного модуля: {yearly_output_per_module:.2f} кВт·ч"
        messagebox.showinfo("Результат", result_text)

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))



def open_solar_panel_parameters_window():
    solar_params_window = tk.Toplevel()
    solar_params_window.title("Параметры солнечной батареи")
    solar_params_window.geometry("500x250")
    
    modules_label = tk.Label(solar_params_window, text="Количество модулей в солнечной батарее:")
    modules_label.grid(row=0, column=0, padx=10, pady=5)
    modules_entry = tk.Entry(solar_params_window)
    modules_entry.grid(row=0, column=1, padx=10, pady=5)

    nominal_power_label = tk.Label(solar_params_window, text="Номинальная мощность модуля, Вт:")
    nominal_power_label.grid(row=1, column=0, padx=10, pady=5)
    nominal_power_entry = tk.Entry(solar_params_window)
    nominal_power_entry.grid(row=1, column=1, padx=10, pady=5)

    radiation_label = tk.Label(solar_params_window, text="Радиация в день, кВт·ч:")
    radiation_label.grid(row=2, column=0, padx=10, pady=5)
    radiation_entry = tk.Entry(solar_params_window)
    radiation_entry.grid(row=2, column=1, padx=10, pady=5)

    calculate_button = tk.Button(solar_params_window, text="Рассчитать", command=lambda: calculate_solar_panel_output(modules_entry.get(), nominal_power_entry.get(), radiation_entry.get()))
    calculate_button.grid(row=3, columnspan=2, pady=10)






def open_wind_turbine_parameters_window():
    wind_turbine_params_window = tk.Toplevel()
    wind_turbine_params_window.title("Параметры ветроэнергетической установки")
    wind_turbine_params_window.geometry("500x300")
    
    
    # Метка и поле для ввода мощности ветрогенератора
    power_label = tk.Label(wind_turbine_params_window, text="Мощность ветрогенератора (кВт/сутки):")
    power_label.grid(row=0, column=0, padx=10, pady=5)
    power_entry = tk.Entry(wind_turbine_params_window)
    power_entry.grid(row=0, column=1, padx=10, pady=5)

    # Метка и поле для ввода стоимости установки
    cost_label = tk.Label(wind_turbine_params_window, text="Стоимость установки (руб.):")
    cost_label.grid(row=1, column=0, padx=10, pady=5)
    cost_entry = tk.Entry(wind_turbine_params_window)
    cost_entry.grid(row=1, column=1, padx=10, pady=5)

    # Метка и поле для ввода цены за киловатт
    cost_per_kWh_label = tk.Label(wind_turbine_params_window, text="Цена за киловатт (руб.):")
    cost_per_kWh_label.grid(row=2, column=0, padx=10, pady=5)
    cost_per_kWh_entry = tk.Entry(wind_turbine_params_window)
    cost_per_kWh_entry.grid(row=2, column=1, padx=10, pady=5)

    # Метка и поле для ввода срока службы
    service_life_label = tk.Label(wind_turbine_params_window, text="Срок службы (лет):")
    service_life_label.grid(row=3, column=0, padx=10, pady=5)
    service_life_entry = tk.Entry(wind_turbine_params_window)
    service_life_entry.grid(row=3, column=1, padx=10, pady=5)

    # Метка и поле для ввода расходов на обслуживание и эксплуатацию
    maintenance_cost_label = tk.Label(wind_turbine_params_window, text="Расходы на обслуживание и эксплуатацию (руб./год):")
    maintenance_cost_label.grid(row=4, column=0, padx=10, pady=5)
    maintenance_cost_entry = tk.Entry(wind_turbine_params_window)
    maintenance_cost_entry.grid(row=4, column=1, padx=10, pady=5)

    # Кнопка для запуска расчета
    calculate_button = tk.Button(wind_turbine_params_window, text="Рассчитать", command=lambda: calculate_wind_turbine_economics(power_entry.get(), cost_per_kWh_entry.get(), cost_entry.get(), service_life_entry.get(), maintenance_cost_entry.get()))
    calculate_button.grid(row=5, columnspan=2, pady=10)
def calculate_wind_turbine_economics(power, cost_per_kWh, cost, service_life, maintenance_cost):
    try:
        # Преобразование введенных значений в нужный формат
        power = float(power)
        cost_per_kWh = float(cost_per_kWh)
        cost = float(cost)
        service_life = int(service_life)
        maintenance_cost = float(maintenance_cost)

        # Расчет общих затрат за срок службы
        total_cost = cost + (maintenance_cost * service_life)

        # Расчет среднегодовых затрат
        average_annual_cost = total_cost / service_life


        # Расчет годового дохода от ветрогенератора
        annual_income = power * cost_per_kWh * 365  # Годовой доход = мощность * стоимость кВт-ч * количество дней в году

        # Расчет прибыли в год
        annual_profit = annual_income - average_annual_cost

        # Расчет прибыли на весь срок службы
        total_profit = annual_profit * service_life

        # Проверка на целесообразность строительства
        if average_annual_cost <= annual_income:
            messagebox.showinfo("Информация", f"Строительство ветрогенератора целесообразно.\nПрибыль в год: {annual_profit:.2f} руб.\nПрибыль за весь срок службы: {total_profit:.2f} руб.")
        else:
            messagebox.showinfo("Информация", f"Строительство ветрогенератора нецелесообразно.\nПрибыль в год: {annual_profit:.2f} руб.\nПрибыль за весь срок службы: {total_profit:.2f} руб.")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))










def calculate_wind_turbine_parameters(power, average_wind_speed, number_of_blades):
    try:
        # Преобразование введенных значений в нужный формат
        power = float(power)
        average_wind_speed = float(average_wind_speed)
        number_of_blades = int(number_of_blades)
        air_density = 1.225  # Плотность воздуха, кг/м^3
        wind_speed = 3  # Средняя скорость ветра, м/с
        air_density = 1.225  # Плотность воздуха, кг/м^3
        filling_coefficient = 0.3  # Коэффициент заполняемости
        
        # Расчет параметров ВЭУ
        rotor_diameter = math.sqrt(power / (0.5 * air_density * wind_speed**3 * filling_coefficient))
        swept_area = 3.14 * (rotor_diameter / 2) ** 2
        aspect_ratio = rotor_diameter / (number_of_blades * 2)
        solidity_factor = number_of_blades / swept_area
        blade_area = swept_area / number_of_blades
        blade_length = (blade_area / aspect_ratio) ** 0.5

        # Возвращаем рассчитанные параметры ВЭУ
        return {
            'rotor_diameter': round(rotor_diameter, 2),
            'swept_area': round(swept_area, 2),
            'aspect_ratio': round(aspect_ratio, 2),
            'solidity_factor': round(solidity_factor, 2),
            'blade_area': round(blade_area, 2),
            'blade_length': round(blade_length, 2)
        }

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def open_wind_turbine_parameters_window():
    wind_turbine_params_window = tk.Toplevel()
    wind_turbine_params_window.title("Параметры ветроэнергетической установки")

    # Метка и поле для ввода мощности ветрогенератора
    power_label = tk.Label(wind_turbine_params_window, text="Мощность ветрогенератора (кВт):")
    power_label.grid(row=0, column=0, padx=10, pady=5)
    power_entry = tk.Entry(wind_turbine_params_window)
    power_entry.grid(row=0, column=1, padx=10, pady=5)

    # Метка и поле для ввода средней скорости ветра в регионе
    average_wind_speed_label = tk.Label(wind_turbine_params_window, text="Средняя скорость ветра в регионе (м/с):")
    average_wind_speed_label.grid(row=1, column=0, padx=10, pady=5)
    average_wind_speed_entry = tk.Entry(wind_turbine_params_window)
    average_wind_speed_entry.grid(row=1, column=1, padx=10, pady=5)

    # Метка и поле для ввода количества лопастей
    number_of_blades_label = tk.Label(wind_turbine_params_window, text="Количество лопастей:")
    number_of_blades_label.grid(row=2, column=0, padx=10, pady=5)
    number_of_blades_entry = tk.Entry(wind_turbine_params_window)
    number_of_blades_entry.grid(row=2, column=1, padx=10, pady=5)

    # Кнопка для запуска расчета
    calculate_button = tk.Button(wind_turbine_params_window, text="Рассчитать", command=lambda: display_calculated_parameters(power_entry.get(), average_wind_speed_entry.get(), number_of_blades_entry.get()))
    calculate_button.grid(row=3, columnspan=2, pady=10)

def display_calculated_parameters(power, average_wind_speed, number_of_blades):
    # Вызываем функцию расчета параметров ВЭУ
    parameters = calculate_wind_turbine_parameters(power, average_wind_speed, number_of_blades)
    if parameters:
        # Отображаем рассчитанные параметры
        result_text = f"Рассчитанные параметры ВЭУ:\n"
        result_text += f"Диаметр ротора: {parameters['rotor_diameter']} м\n"
        result_text += f"Ометаемая площадь ротора: {parameters['swept_area']} м²\n"
        result_text += f"Относительное удлинение: {parameters['aspect_ratio']}\n"
        result_text += f"Коэффициент заполняемости: {parameters['solidity_factor']}\n"
        result_text += f"Площадь лопасти: {parameters['blade_area']} м²\n"
        result_text += f"Длина лопасти: {parameters['blade_length']} м"
        messagebox.showinfo("Рассчитанные параметры", result_text)





































# Загружаем сохраненные значения при запуске программы
load_values()

# Создаем функцию закрытия окна
def on_closing():
    # Получаем текущие значения из полей ввода
    speed = speed_entry.get()
    radius = radius_entry.get()
    generator_efficiency = generator_eff_entry.get()
    gearbox_efficiency = gearbox_eff_entry.get()
    # Сохраняем введенные значения перед закрытием
    save_values(speed, radius, generator_efficiency, gearbox_efficiency)
    # Закрываем окно
    root.destroy()

# Привязываем функцию закрытия окна к событию закрытия окна
root.protocol("WM_DELETE_WINDOW", on_closing)

# Запускаем главный цикл программы
root.mainloop()
