import os
import sys
from datetime import datetime, date
from database import DatabaseManager
from auth import AuthManager
from export_data import DataExporter
from backup import BackupManager
from seed_data import seed_database, create_test_users
from models import *

class MedicalClinicApp:
    """Главный класс приложения медицинской клиники"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager(self.db_manager)
        self.current_user = None
        self.exporter = None
        self.backup_manager = None
        self.session = None
        
    def init_application(self):
        """Инициализация приложения"""
        print("=" * 60)
        print("МЕДИЦИНСКАЯ КЛИНИКА - СИСТЕМА УПРАВЛЕНИЯ")
        print("=" * 60)
        
        # Инициализация базы данных
        Session = self.db_manager.init_database()
        self.session = Session()
        
        # Создание администратора по умолчанию
        self.auth_manager.create_default_admin()
        
        # Инициализация менеджеров
        self.exporter = DataExporter(self.session)
        self.backup_manager = BackupManager()
        
        # Заполнение тестовыми данными (если база пустая)
        if not self._has_data():
            print("\nБаза данных пуста. Заполняем тестовыми данными...")
            if seed_database(self.session):
                create_test_users(self.auth_manager)
                print("Тестовые данные успешно добавлены!")
        
        print("\nСистема готова к работе!")
    
    def _has_data(self):
        """Проверка наличия данных в базе"""
        try:
            # Проверяем наличие пациентов
            patient_count = self.session.query(Patient).count()
            return patient_count > 0
        except:
            return False
    
    def clear_screen(self):
        """Очистка экрана консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Печать заголовка"""
        self.clear_screen()
        print("=" * 60)
        print(f"{title:^60}")
        print("=" * 60)
        if self.current_user:
            print(f"Пользователь: {self.current_user['username']} ({self.current_user['role']})")
            print("-" * 60)
    
    def login_menu(self):
        """Меню входа в систему"""
        while True:
            self.print_header("ВХОД В СИСТЕМУ")
            
            print("\nВведите учетные данные:")
            username = input("Логин: ").strip()
            password = input("Пароль: ").strip()
            
            success, message, user_info = self.auth_manager.login(username, password)
            
            if success:
                self.current_user = user_info
                print(f"\n✓ {message}")
                input("\nНажмите Enter для продолжения...")
                return True
            else:
                print(f"\n✗ {message}")
                
                choice = input("\nПопробовать снова? (д/н): ").lower()
                if choice != 'д':
                    return False
    
    def main_menu(self):
        """Главное меню приложения"""
        while True:
            self.print_header("ГЛАВНОЕ МЕНЮ")
            
            print("\nДоступные действия:")
            
            # Общие функции для всех ролей
            print("1. 📊 Просмотр информации")
            print("2. 📤 Экспорт данных")
            print("3. 💾 Резервное копирование")
            
            # Функции в зависимости от роли
            if self.current_user['role'] in ['admin', 'registrar']:
                print("4. 👥 Управление записями на прием")
            
            if self.current_user['role'] in ['admin', 'doctor']:
                print("5. 🏥 Медицинские записи")
            
            if self.current_user['role'] == 'admin':
                print("6. ⚙️ Управление системой")
            
            print("7. 👤 Сменить пользователя")
            print("0. 🚪 Выход")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == '1':
                self.view_information_menu()
            elif choice == '2':
                self.export_menu()
            elif choice == '3':
                self.backup_menu()
            elif choice == '4' and self.current_user['role'] in ['admin', 'registrar']:
                self.appointment_management_menu()
            elif choice == '5' and self.current_user['role'] in ['admin', 'doctor']:
                self.medical_records_menu()
            elif choice == '6' and self.current_user['role'] == 'admin':
                self.system_management_menu()
            elif choice == '7':
                if self.auth_manager.logout():
                    self.current_user = None
                    print("Выход выполнен успешно")
                    input("Нажмите Enter для продолжения...")
                    return True  # Вернуться к меню входа
            elif choice == '0':
                print("Выход из системы...")
                return False
            else:
                print("Неверный выбор!")
                input("Нажмите Enter для продолжения...")
    
    def view_information_menu(self):
        """Меню просмотра информации"""
        while True:
            self.print_header("ПРОСМОТР ИНФОРМАЦИИ")
            
            print("\nДоступная информация:")
            print("1. 📅 Расписание врачей")
            print("2. 👥 Список пациентов")
            print("3. 🩺 Список врачей")
            print("4. 📋 Мои записи на прием")
            print("5. 📊 Статистика клиники")
            print("0. ↩️ Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == '1':
                self.view_schedule()
            elif choice == '2':
                self.view_patients()
            elif choice == '3':
                self.view_doctors()
            elif choice == '4':
                self.view_my_appointments()
            elif choice == '5':
                self.view_statistics()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")
                input("Нажмите Enter для продолжения...")
    
    def view_schedule(self):
        """Просмотр расписания врачей"""
        self.print_header("РАСПИСАНИЕ ВРАЧЕЙ")
        
        try:
            # Получаем расписание на ближайшие 7 дней
            from datetime import timedelta
            today = date.today()
            next_week = today + timedelta(days=7)
            
            schedules = self.session.query(Schedule).filter(
                Schedule.work_date >= today,
                Schedule.work_date <= next_week
            ).order_by(Schedule.work_date, Schedule.start_time).all()
            
            if not schedules:
                print("Расписание на ближайшую неделю не найдено.")
                input("\nНажмите Enter для продолжения...")
                return
            
            # Группируем по датам
            schedule_by_date = {}
            for schedule in schedules:
                date_str = schedule.work_date.strftime("%d.%m.%Y")
                if date_str not in schedule_by_date:
                    schedule_by_date[date_str] = []
                schedule_by_date[date_str].append(schedule)
            
            # Выводим расписание
            for date_str, day_schedules in schedule_by_date.items():
                print(f"\n📅 {date_str}:")
                print("-" * 60)
                print(f"{'Время':<12} {'Врач':<25} {'Кабинет':<10} {'Свободно':<10}")
                print("-" * 60)
                
                for schedule in day_schedules:
                    doctor_name = schedule.employee.full_name if schedule.employee else "Не указан"
                    time_str = f"{schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}"
                    
                    print(f"{time_str:<12} {doctor_name:<25} {schedule.cabinet_number or '':<10} {schedule.available_slots:<10}")
        
        except Exception as e:
            print(f"Ошибка при получении расписания: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def view_patients(self):
        """Просмотр списка пациентов"""
        self.print_header("СПИСОК ПАЦИЕНТОВ")
        
        try:
            patients = self.session.query(Patient).order_by(Patient.last_name, Patient.first_name).all()
            
            if not patients:
                print("Пациенты не найдены.")
                input("\nНажмите Enter для продолжения...")
                return
            
            print(f"{'ID':<5} {'ФИО':<30} {'Дата рождения':<15} {'Телефон':<15} {'Email':<20}")
            print("-" * 90)
            
            for patient in patients:
                print(f"{patient.id:<5} {patient.full_name:<30} "
                      f"{patient.birth_date.strftime('%d.%m.%Y') if patient.birth_date else '':<15} "
                      f"{patient.phone or '':<15} {patient.email or '':<20}")
            
            print(f"\nВсего пациентов: {len(patients)}")
        
        except Exception as e:
            print(f"Ошибка при получении пациентов: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def view_doctors(self):
        """Просмотр списка врачей"""
        self.print_header("СПИСОК ВРАЧЕЙ")
        
        try:
            from models import Position
            doctors = self.session.query(Employee).join(Position).filter(
                Position.name.ilike('%врач%')
            ).order_by(Employee.last_name, Employee.first_name).all()
            
            if not doctors:
                print("Врачи не найдены.")
                input("\nНажмите Enter для продолжения...")
                return
            
            print(f"{'ID':<5} {'ФИО':<30} {'Должность':<20} {'Специализация':<20} {'Кабинет':<10}")
            print("-" * 90)
            
            for doctor in doctors:
                position_name = doctor.position.name if doctor.position else ""
                specialization_name = doctor.specialization.name if doctor.specialization else ""
                
                print(f"{doctor.id:<5} {doctor.full_name:<30} "
                      f"{position_name:<20} {specialization_name:<20} {doctor.cabinet_number or '':<10}")
            
            print(f"\nВсего врачей: {len(doctors)}")
        
        except Exception as e:
            print(f"Ошибка при получении врачей: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def view_my_appointments(self):
        """Просмотр своих записей на прием"""
        self.print_header("МОИ ЗАПИСИ НА ПРИЕМ")
        
        try:
            if self.current_user['role'] == 'patient' and 'patient_id' in self.current_user:
                # Для пациентов - показываем их записи
                appointments = self.session.query(Appointment).filter(
                    Appointment.patient_id == self.current_user['patient_id']
                ).order_by(Appointment.appointment_date.desc()).all()
            elif self.current_user['role'] == 'doctor' and 'employee_id' in self.current_user:
                # Для врачей - показываем записи к ним
                appointments = self.session.query(Appointment).filter(
                    Appointment.doctor_id == self.current_user['employee_id']
                ).order_by(Appointment.appointment_date.desc()).all()
            else:
                # Для остальных - показываем все записи
                appointments = self.session.query(Appointment).order_by(Appointment.appointment_date.desc()).limit(20).all()
            
            if not appointments:
                print("Записи на прием не найдены.")
                input("\nНажмите Enter для продолжения...")
                return
            
            print(f"{'ID':<5} {'Дата':<12} {'Время':<8} {'Пациент':<25} {'Врач':<25} {'Статус':<15}")
            print("-" * 90)
            
            for appt in appointments:
                patient_name = appt.patient.full_name if appt.patient else "Не указан"
                doctor_name = appt.doctor.full_name if appt.doctor else "Не указан"
                status = appt.status.value if appt.status else "Не указан"
                
                print(f"{appt.id:<5} "
                      f"{appt.appointment_date.strftime('%d.%m.%Y') if appt.appointment_date else '':<12} "
                      f"{str(appt.appointment_time) if appt.appointment_time else '':<8} "
                      f"{patient_name:<25} {doctor_name:<25} {status:<15}")
            
            print(f"\nВсего записей: {len(appointments)}")
        
        except Exception as e:
            print(f"Ошибка при получении записей: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def view_statistics(self):
        """Просмотр статистики клиники"""
        self.print_header("СТАТИСТИКА КЛИНИКИ")
        
        try:
            from sqlalchemy import func
            
            # Количество пациентов
            patient_count = self.session.query(Patient).count()
            
            # Количество врачей
            from models import Position
            doctor_count = self.session.query(Employee).join(Position).filter(
                Position.name.ilike('%врач%')
            ).count()
            
            # Количество записей
            appointment_count = self.session.query(Appointment).count()
            
            # Записи по статусам
            status_stats = self.session.query(
                Appointment.status, 
                func.count(Appointment.id)
            ).group_by(Appointment.status).all()
            
            # Количество медицинских записей
            record_count = self.session.query(MedicalRecord).count()
            
            print("📊 ОБЩАЯ СТАТИСТИКА")
            print("-" * 40)
            print(f"👥 Пациентов: {patient_count}")
            print(f"🩺 Врачей: {doctor_count}")
            print(f"📅 Записей на прием: {appointment_count}")
            print(f"🏥 Медицинских записей: {record_count}")
            
            print("\n📈 СТАТУСЫ ЗАПИСЕЙ НА ПРИЕМ")
            print("-" * 40)
            for status, count in status_stats:
                status_name = status.value if status else "Не указан"
                print(f"{status_name}: {count}")
            
            # Статистика по возрасту пациентов
            print("\n👴 ВОЗРАСТНАЯ СТАТИСТИКА ПАЦИЕНТОВ")
            print("-" * 40)
            
            # Группируем по возрастным категориям
            age_categories = {
                'Дети (0-17)': 0,
                'Молодые (18-35)': 0,
                'Средний возраст (36-60)': 0,
                'Пожилые (61+)': 0
            }
            
            patients = self.session.query(Patient).all()
            for patient in patients:
                if patient.age is not None:
                    if patient.age <= 17:
                        age_categories['Дети (0-17)'] += 1
                    elif patient.age <= 35:
                        age_categories['Молодые (18-35)'] += 1
                    elif patient.age <= 60:
                        age_categories['Средний возраст (36-60)'] += 1
                    else:
                        age_categories['Пожилые (61+)'] += 1
            
            for category, count in age_categories.items():
                if patient_count > 0:
                    percentage = (count / patient_count) * 100
                    print(f"{category}: {count} ({percentage:.1f}%)")
                else:
                    print(f"{category}: {count}")
        
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def export_menu(self):
        """Меню экспорта данных"""
        while True:
            self.print_header("ЭКСПОРТ ДАННЫХ")
            
            print("\nДоступные форматы экспорта:")
            print("1. 📄 JSON - Экспорт записей на прием")
            print("2. 📊 CSV - Экспорт пациентов")
            print("3. 📑 PDF - Экспорт расписания")
            print("4. 📝 DOCX - Экспорт медицинских записей")
            print("5. 📈 XLSX - Экспорт статистики")
            print("6. 🚀 Экспорт во все форматы")
            print("0. ↩️ Назад")
            
            choice = input("\nВыберите формат: ").strip()
            
            if choice == '1':
                self.export_to_json()
            elif choice == '2':
                self.export_to_csv()
            elif choice == '3':
                self.export_to_pdf()
            elif choice == '4':
                self.export_to_docx()
            elif choice == '5':
                self.export_to_xlsx()
            elif choice == '6':
                self.export_to_all()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")
                input("Нажмите Enter для продолжения...")
    
    def export_to_json(self):
        """Экспорт в JSON"""
        self.print_header("ЭКСПОРТ В JSON")
        
        try:
            # Запрос параметров фильтрации
            print("\nПараметры экспорта:")
            start_date = input("Дата начала (ГГГГ-ММ-ДД, Enter для пропуска): ").strip()
            end_date = input("Дата окончания (ГГГГ-ММ-ДД, Enter для пропуска): ").strip()
            doctor_id = input("ID врача (Enter для пропуска): ").strip()
            
            # Преобразование параметров
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
            doctor_id_int = int(doctor_id) if doctor_id else None
            
            success, message, filepath = self.exporter.export_appointments_to_json(
                start_date_obj, end_date_obj, doctor_id_int
            )
            
            if success:
                print(f"\n✓ {message}")
                print(f"Файл: {filepath}")
            else:
                print(f"\n✗ {message}")
        
        except ValueError:
            print("Ошибка: Неверный формат даты или ID")
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def export_to_csv(self):
        """Экспорт в CSV"""
        self.print_header("ЭКСПОРТ В CSV")
        
        try:
            print("\nПараметры экспорта:")
            min_age = input("Минимальный возраст (Enter для пропуска): ").strip()
            max_age = input("Максимальный возраст (Enter для пропуска): ").strip()
            
            # Преобразование параметров
            min_age_int = int(min_age) if min_age else None
            max_age_int = int(max_age) if max_age else None
            
            success, message, filepath = self.exporter.export_patients_to_csv(min_age_int, max_age_int)
            
            if success:
                print(f"\n✓ {message}")
                print(f"Файл: {filepath}")
            else:
                print(f"\n✗ {message}")
        
        except ValueError:
            print("Ошибка: Неверный формат возраста")
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def export_to_pdf(self):
        """Экспорт в PDF"""
        self.print_header("ЭКСПОРТ В PDF")
        
        try:
            print("\nПараметры экспорта:")
            doctor_id = input("ID врача (Enter для всех): ").strip()
            start_date = input("Дата начала (ГГГГ-ММ-ДД, Enter для пропуска): ").strip()
            end_date = input("Дата окончания (ГГГГ-ММ-ДД, Enter для пропуска): ").strip()
            
            # Преобразование параметров
            doctor_id_int = int(doctor_id) if doctor_id else None
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
            
            success, message, filepath = self.exporter.export_schedule_to_pdf(doctor_id_int, start_date_obj, end_date_obj)
            
            if success:
                print(f"\n✓ {message}")
                print(f"Файл: {filepath}")
            else:
                print(f"\n✗ {message}")
        
        except ValueError:
            print("Ошибка: Неверный формат даты или ID")
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def export_to_docx(self):
        """Экспорт в DOCX"""
        self.print_header("ЭКСПОРТ В DOCX")
        
        try:
            print("\nПараметры экспорта:")
            patient_id = input("ID пациента (Enter для всех): ").strip()
            doctor_id = input("ID врача (Enter для всех): ").strip()
            
            # Преобразование параметров
            patient_id_int = int(patient_id) if patient_id else None
            doctor_id_int = int(doctor_id) if doctor_id else None
            
            success, message, filepath = self.exporter.export_medical_records_to_docx(patient_id_int, doctor_id_int)
            
            if success:
                print(f"\n✓ {message}")
                print(f"Файл: {filepath}")
            else:
                print(f"\n✗ {message}")
        
        except ValueError:
            print("Ошибка: Неверный формат ID")
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def export_to_xlsx(self):
        """Экспорт в XLSX"""
        self.print_header("ЭКСПОРТ В XLSX")
        
        try:
            success, message, filepath = self.exporter.export_statistics_to_xlsx()
            
            if success:
                print(f"\n✓ {message}")
                print(f"Файл: {filepath}")
            else:
                print(f"\n✗ {message}")
        
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def export_to_all(self):
        """Экспорт во все форматы"""
        self.print_header("ЭКСПОРТ ВО ВСЕ ФОРМАТЫ")
        
        print("\nЗапуск экспорта во все доступные форматы...")
        
        results = self.exporter.export_all_formats()
        
        print("\nРезультаты экспорта:")
        print("-" * 60)
        
        for format_name, success, message, filepath in results:
            status = "✓" if success else "✗"
            print(f"{status} {format_name}: {message}")
            if filepath:
                print(f"   Файл: {filepath}")
        
        input("\nНажмите Enter для продолжения...")
    
    def backup_menu(self):
        """Меню резервного копирования"""
        while True:
            self.print_header("РЕЗЕРВНОЕ КОПИРОВАНИЕ")
            
            print("\nДоступные действия:")
            print("1. 💾 Создать резервную копию")
            print("2. 📋 Список резервных копий")
            print("3. 🔄 Восстановить из резервной копии")
            print("4. ⏰ Настроить автоматическое копирование")
            print("0. ↩️ Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == '1':
                self.create_backup()
            elif choice == '2':
                self.list_backups()
            elif choice == '3':
                self.restore_backup()
            elif choice == '4':
                self.schedule_backup()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")
                input("Нажмите Enter для продолжения...")
    
    def create_backup(self):
        """Создание резервной копии"""
        self.print_header("СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ")
        
        print("\nТип резервного копирования:")
        print("1. 💻 Локальное (на этот компьютер)")
        print("2. 🌐 Удаленное (имитация)")
        print("3. ☁️ Облачное (имитация)")
        
        choice = input("\nВыберите тип: ").strip()
        
        backup_type = 'local'
        if choice == '1':
            backup_type = 'local'
        elif choice == '2':
            backup_type = 'remote'
        elif choice == '3':
            backup_type = 'cloud'
        else:
            print("Неверный выбор!")
            input("Нажмите Enter для продолжения...")
            return
        
        success, message = self.backup_manager.create_backup(backup_type)
        
        if success:
            print(f"\n✓ {message}")
        else:
            print(f"\n✗ {message}")
        
        input("\nНажмите Enter для продолжения...")
    
    def list_backups(self):
        """Список резервных копий"""
        self.print_header("СПИСОК РЕЗЕРВНЫХ КОПИЙ")
        
        backups = self.backup_manager.list_backups()
        
        if not backups:
            print("Резервные копии не найдены.")
        else:
            print(f"{'№':<3} {'Имя файла':<30} {'Размер (МБ)':<12} {'Дата создания':<20}")
            print("-" * 70)
            
            for i, backup in enumerate(backups, 1):
                print(f"{i:<3} {backup['filename']:<30} {backup['size_mb']:<12.2f} {backup['created']:<20}")
        
        input("\nНажмите Enter для продолжения...")
    
    def restore_backup(self):
        """Восстановление из резервной копии"""
        self.print_header("ВОССТАНОВЛЕНИЕ ИЗ РЕЗЕРВНОЙ КОПИИ")
        
        backups = self.backup_manager.list_backups()
        
        if not backups:
            print("Резервные копии не найдены.")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Доступные резервные копии:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup['filename']} ({backup['created']})")
        
        try:
            choice = input("\nВыберите номер копии для восстановления (0 для отмены): ").strip()
            
            if choice == '0':
                return
            
            index = int(choice) - 1
            if 0 <= index < len(backups):
                confirm = input(f"\nВосстановить из {backups[index]['filename']}? (д/н): ").lower()
                
                if confirm == 'д':
                    success, message = self.backup_manager.restore_backup(backups[index]['filename'])
                    
                    if success:
                        print(f"\n✓ {message}")
                        print("Перезапустите приложение для применения изменений.")
                    else:
                        print(f"\n✗ {message}")
                else:
                    print("Восстановление отменено.")
            else:
                print("Неверный номер!")
        
        except ValueError:
            print("Неверный ввод!")
        except Exception as e:
            print(f"Ошибка восстановления: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def schedule_backup(self):
        """Настройка автоматического резервного копирования"""
        self.print_header("АВТОМАТИЧЕСКОЕ РЕЗЕРВНОЕ КОПИРОВАНИЕ")
        
        print("\nНастройка автоматического копирования:")
        
        try:
            interval = input("Интервал (часы, по умолчанию 24): ").strip()
            interval_hours = int(interval) if interval else 24
            
            print("\nТип копирования:")
            print("1. 💻 Локальное")
            print("2. 🌐 Удаленное (имитация)")
            
            type_choice = input("Выберите тип: ").strip()
            backup_type = 'local' if type_choice == '1' else 'remote'
            
            success, message = self.backup_manager.schedule_backup(interval_hours, backup_type)
            
            if success:
                print(f"\n✓ {message}")
            else:
                print(f"\n✗ {message}")
        
        except ValueError:
            print("Неверный формат интервала!")
        except Exception as e:
            print(f"Ошибка настройки: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def appointment_management_menu(self):
        """Меню управления записями на прием"""
        while True:
            self.print_header("УПРАВЛЕНИЕ ЗАПИСЯМИ НА ПРИЕМ")
            
            print("\nДоступные действия:")
            print("1. 📝 Создать новую запись")
            print("2. ✏️ Изменить запись")
            print("3. ❌ Отменить запись")
            print("4. 🔍 Поиск записей")
            print("0. ↩️ Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == '1':
                self.create_appointment()
            elif choice == '2':
                self.edit_appointment()
            elif choice == '3':
                self.cancel_appointment()
            elif choice == '4':
                self.search_appointments()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")
                input("Нажмите Enter для продолжения...")
    
    def create_appointment(self):
        """Создание новой записи на прием"""
        self.print_header("СОЗДАНИЕ НОВОЙ ЗАПИСИ")
        
        try:
            # Запрос данных
            patient_id = input("ID пациента: ").strip()
            doctor_id = input("ID врача: ").strip()
            appointment_date = input("Дата приема (ГГГГ-ММ-ДД): ").strip()
            appointment_time = input("Время приема (ЧЧ:ММ): ").strip()
            reason = input("Причина приема: ").strip()
            
            # Проверка существования пациента и врача
            patient = self.session.query(Patient).filter_by(id=int(patient_id)).first()
            doctor = self.session.query(Employee).filter_by(id=int(doctor_id)).first()
            
            if not patient:
                print("Пациент не найден!")
                input("\nНажмите Enter для продолжения...")
                return
            
            if not doctor:
                print("Врач не найден!")
                input("\nНажмите Enter для продолжения...")
                return
            
            # Создание записи
            new_appointment = Appointment(
                patient_id=int(patient_id),
                doctor_id=int(doctor_id),
                appointment_date=datetime.strptime(appointment_date, "%Y-%m-%d").date(),
                appointment_time=datetime.strptime(appointment_time, "%H:%M").time(),
                reason=reason,
                status=AppointmentStatus.SCHEDULED,
                created_at=datetime.now()
            )
            
            # Поиск подходящего расписания
            schedule = self.session.query(Schedule).filter(
                Schedule.employee_id == int(doctor_id),
                Schedule.work_date == new_appointment.appointment_date,
                Schedule.start_time <= new_appointment.appointment_time,
                Schedule.end_time > new_appointment.appointment_time,
                Schedule.available_slots > 0
            ).first()
            
            if schedule:
                new_appointment.schedule_id = schedule.id
                
                self.session.add(new_appointment)
                self.session.commit()
                
                print(f"\n✓ Запись создана успешно!")
                print(f"ID записи: {new_appointment.id}")
            else:
                print("\n✗ Нет свободных слотов в расписании на выбранное время!")
        
        except ValueError as e:
            print(f"Ошибка ввода данных: {e}")
        except Exception as e:
            print(f"Ошибка создания записи: {e}")
            self.session.rollback()
        
        input("\nНажмите Enter для продолжения...")
    
    def medical_records_menu(self):
        """Меню управления медицинскими записями"""
        while True:
            self.print_header("МЕДИЦИНСКИЕ ЗАПИСИ")
            
            print("\nДоступные действия:")
            print("1. 📖 Просмотр медицинских записей")
            print("2. ✍️ Создать медицинскую запись")
            print("3. 💊 Добавить назначение")
            print("0. ↩️ Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == '1':
                self.view_medical_records()
            elif choice == '2':
                self.create_medical_record()
            elif choice == '3':
                self.add_prescription()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")
                input("Нажмите Enter для продолжения...")
    
    def system_management_menu(self):
        """Меню управления системой (только для администраторов)"""
        while True:
            self.print_header("УПРАВЛЕНИЕ СИСТЕМОЙ")
            
            print("\nДоступные действия:")
            print("1. 👥 Управление пользователями")
            print("2. 🗃️ Управление справочниками")
            print("3. 🧹 Очистка базы данных")
            print("4. 🔄 Пересоздать тестовые данные")
            print("0. ↩️ Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == '1':
                self.user_management_menu()
            elif choice == '2':
                self.reference_management_menu()
            elif choice == '3':
                self.clean_database()
            elif choice == '4':
                self.recreate_test_data()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")
                input("Нажмите Enter для продолжения...")
    
    def run(self):
        """Запуск приложения"""
        try:
            self.init_application()
            
            # Основной цикл приложения
            while True:
                if not self.current_user:
                    if not self.login_menu():
                        break
                
                if not self.main_menu():
                    break
            
            # Завершение работы
            print("\nСпасибо за использование системы!")
            if self.session:
                self.db_manager.close_session(self.session)
        
        except KeyboardInterrupt:
            print("\n\nПриложение завершено пользователем.")
        except Exception as e:
            print(f"\nКритическая ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.session:
                self.db_manager.close_session(self.session)

# Точка входа в приложение
if __name__ == "__main__":
    app = MedicalClinicApp()
    app.run()