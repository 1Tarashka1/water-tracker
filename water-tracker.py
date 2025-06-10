import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class WaterTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Tracker")
        self.root.geometry("500x600")
        self.root.option_add('*Font', 'Arial 12')
        
        # Инициализация данных
        self.data_file = "water_data.json"
        self.history_file = "water_history.json"
        self.daily_goal = 2000  # мл
        self.current_intake = 0
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        self.update_display()
    
    def load_data(self):
        """Загрузка данных из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.current_intake = data.get('current_intake', 0)
                    self.daily_goal = data.get('daily_goal', 2000)
            except:
                self.current_intake = 0
                self.daily_goal = 2000
        
        self.history = {}
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = {}
        
        if self.today not in self.history:
            self.history[self.today] = self.current_intake
    
    def save_data(self):
        """Сохранение данных в файл"""
        data = {
            'current_intake': self.current_intake,
            'daily_goal': self.daily_goal
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f)
        
        self.history[self.today] = self.current_intake
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Заголовок
        self.title_label = tk.Label(
            main_frame, 
            text="💧 Трекер воды",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Текущее потребление
        self.intake_label = tk.Label(
            main_frame, 
            text="0 / 2000 мл",
            font=("Arial", 24)
        )
        self.intake_label.pack(pady=15)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(
            main_frame, 
            orient="horizontal", 
            length=300, 
            mode="determinate"
        )
        self.progress.pack(pady=10)
        
        # Кнопки добавления воды
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame, 
            text="+100 мл", 
            command=lambda: self.add_water(100),
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame, 
            text="+250 мл", 
            command=lambda: self.add_water(250),
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame, 
            text="+500 мл", 
            command=lambda: self.add_water(500),
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Ручной ввод
        custom_frame = tk.Frame(main_frame)
        custom_frame.pack(pady=10)
        
        self.custom_entry = tk.Entry(custom_frame, width=10)
        self.custom_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            custom_frame, 
            text="Добавить (мл)", 
            command=self.add_custom_water
        ).pack(side=tk.LEFT)
        
        # Настройка цели
        goal_frame = tk.Frame(main_frame)
        goal_frame.pack(pady=10)
        
        tk.Label(goal_frame, text="Цель:").pack(side=tk.LEFT)
        self.goal_entry = tk.Entry(goal_frame, width=8)
        self.goal_entry.insert(0, str(self.daily_goal))
        self.goal_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            goal_frame, 
            text="Обновить", 
            command=self.update_goal
        ).pack(side=tk.LEFT)
        
        # Кнопки управления
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=20)
        
        tk.Button(
            control_frame, 
            text="Сбросить", 
            command=self.reset_intake,
            bg="#ffdddd"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            control_frame, 
            text="Показать график", 
            command=self.show_weekly_chart,
            bg="#ddddff"
        ).pack(side=tk.LEFT, padx=10)
    
    def show_weekly_chart(self):
        """Показать график в отдельном окне"""
        chart_window = tk.Toplevel(self.root)
        chart_window.title("График потребления воды")
        chart_window.geometry("800x500")
        
        # Получаем данные за неделю
        dates = []
        amounts = []
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            dates.append(date)
            amounts.append(self.history.get(date, 0))
        
        dates = dates[::-1]
        amounts = amounts[::-1]
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        bars = ax.bar(dates, amounts, color='#66b3ff')
        ax.axhline(y=self.daily_goal, color='r', linestyle='--', label='Цель')
        
        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)} мл',
                    ha='center', va='bottom')
        
        ax.set_title('Потребление воды за неделю', pad=20, fontsize=16)
        ax.set_ylabel('Мл', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Встраиваем график в окно
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Кнопка закрытия
        tk.Button(
            chart_window, 
            text="Закрыть", 
            command=chart_window.destroy,
            bg="#ffdddd"
        ).pack(pady=10)
    
    def add_water(self, amount):
        """Добавить воду"""
        self.current_intake += amount
        self.update_display()
        self.save_data()
        messagebox.showinfo("Успех", f"Добавлено {amount} мл воды!")
    
    def add_custom_water(self):
        """Добавить произвольное количество воды"""
        try:
            amount = int(self.custom_entry.get())
            if amount > 0:
                self.add_water(amount)
                self.custom_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Ошибка", "Введите положительное число")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число")
    
    def update_goal(self):
        """Обновить дневную цель"""
        try:
            new_goal = int(self.goal_entry.get())
            if new_goal > 0:
                self.daily_goal = new_goal
                self.update_display()
                self.save_data()
                messagebox.showinfo("Успех", f"Новая цель: {new_goal} мл")
            else:
                messagebox.showerror("Ошибка", "Цель должна быть положительной")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число")
    
    def reset_intake(self):
        """Сбросить потребление"""
        if messagebox.askyesno("Подтверждение", "Сбросить потребление воды на сегодня?"):
            self.current_intake = 0
            self.update_display()
            self.save_data()
    
    def update_display(self):
        """Обновить отображение"""
        self.intake_label.config(text=f"{self.current_intake} / {self.daily_goal} мл")
        
        percentage = min(100, (self.current_intake / self.daily_goal) * 100)
        self.progress['value'] = percentage
        
        # Изменяем цвет прогресс-бара
        if percentage < 50:
            self.progress['style'] = 'red.Horizontal.TProgressbar'
        elif percentage < 80:
            self.progress['style'] = 'orange.Horizontal.TProgressbar'
        else:
            self.progress['style'] = 'green.Horizontal.TProgressbar'
    
    def run(self):
        # Стили для прогресс-бара
        style = ttk.Style()
        style.theme_use('default')
        style.configure('red.Horizontal.TProgressbar', background='#ff6b6b')
        style.configure('orange.Horizontal.TProgressbar', background='#ffa502')
        style.configure('green.Horizontal.TProgressbar', background='#2ed573')
        
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterTrackerApp(root)
    app.run()