from models import *
from auth import AuthManager
from database import DatabaseManager
from datetime import datetime, date, time
import random

def seed_database(session):
    """Заполнение базы данных тестовыми данными"""
    
    # 1. Создание должностей
    positions = [
        Position(name='Главный врач', description='Руководитель медицинского учреждения', min_salary=100000, max_salary=200000),
        Position(name='Врач-терапевт', description='Врач общей практики', min_salary=60000, max_salary=120000),
        Position(name='Врач-кардиолог', description='Специалист по заболеваниям сердца', min_salary=80000, max_salary=150000),
        Position(name='Врач-невролог', description='Специалист по заболеваниям нервной системы', min_salary=75000, max_salary=140000),
        Position(name='Врач-хирург', description='Специалист по хирургическим операциям', min_salary=90000, max_salary=160000),
        Position(name='Медсестра', description='Средний медицинский персонал', min_salary=30000, max_salary=60000),
        Position(name='Регистратор', description='Административный персонал', min_salary=25000, max_salary=40000),
        Position(name='Администратор', description='Управление клиникой', min_salary=50000, max_salary=90000),
    ]
    
    for position in positions:
        session.add(position)
    session.commit()
    
    # 2. Создание специализаций
    specializations = [
        Specialization(name='Терапия', description='Общая терапия', category='терапевтическая'),
        Specialization(name='Кардиология', description='Заболевания сердечно-сосудистой системы', category='терапевтическая'),
        Specialization(name='Неврология', description='Заболевания нервной системы', category='терапевтическая'),
        Specialization(name='Хирургия', description='Хирургические заболевания', category='хирургическая'),
        Specialization(name='Педиатрия', description='Детские болезни', category='терапевтическая'),
        Specialization(name='Офтальмология', description='Заболевания глаз', category='терапевтическая'),
        Specialization(name='Стоматология', description='Заболевания зубов и полости рта', category='терапевтическая'),
    ]
    
    for specialization in specializations:
        session.add(specialization)
    session.commit()
    
    # 3. Создание сотрудников
    employees = [
        Employee(
            last_name='Иванов',
            first_name='Александр',
            patronymic='Петрович',
            birth_date=date(1975, 5, 15),
            phone='+7 (911) 123-45-67',
            email='ivanov@clinic.ru',
            hire_date=date(2010, 3, 10),
            cabinet_number='101',
            position_id=1,  # Главный врач
            specialization_id=1,  # Терапия
        ),
        Employee(
            last_name='Петрова',
            first_name='Мария',
            patronymic='Ивановна',
            birth_date=date(1980, 8, 22),
            phone='+7 (911) 234-56-78',
            email='petrova@clinic.ru',
            hire_date=date(2015, 6, 20),
            cabinet_number='102',
            position_id=2,  # Врач-терапевт
            specialization_id=1,  # Терапия
        ),
        Employee(
            last_name='Сидоров',
            first_name='Дмитрий',
            patronymic='Александрович',
            birth_date=date(1985, 3, 30),
            phone='+7 (911) 345-67-89',
            email='sidorov@clinic.ru',
            hire_date=date(2018, 9, 1),
            cabinet_number='103',
            position_id=3,  # Врач-кардиолог
            specialization_id=2,  # Кардиология
        ),
        Employee(
            last_name='Козлова',
            first_name='Елена',
            patronymic='Сергеевна',
            birth_date=date(1990, 11, 5),
            phone='+7 (911) 456-78-90',
            email='kozlova@clinic.ru',
            hire_date=date(2020, 1, 15),
            cabinet_number='201',
            position_id=4,  # Врач-невролог
            specialization_id=3,  # Неврология
        ),
        Employee(
            last_name='Смирнова',
            first_name='Анна',
            patronymic='Владимировна',
            birth_date=date(1992, 7, 18),
            phone='+7 (911) 567-89-01',
            email='smirnova@clinic.ru',
            hire_date=date(2021, 4, 10),
            cabinet_number='001',
            position_id=7,  # Регистратор
            specialization_id=None,
        ),
    ]
    
    for employee in employees:
        session.add(employee)
    session.commit()
    
    # 4. Создание пациентов
    patients = [
        Patient(
            last_name='Васильев',
            first_name='Игорь',
            patronymic='Николаевич',
            birth_date=date(1985, 2, 14),
            gender='М',
            phone='+7 (921) 111-22-33',
            address='ул. Ленина, д. 10, кв. 5',
            passport_series='4501',
            passport_number='123456',
            email='vasiliev@mail.ru',
            registration_date=date(2023, 1, 15),
        ),
        Patient(
            last_name='Николаева',
            first_name='Ольга',
            patronymic='Сергеевна',
            birth_date=date(1990, 6, 25),
            gender='Ж',
            phone='+7 (921) 222-33-44',
            address='ул. Советская, д. 25, кв. 12',
            passport_series='4502',
            passport_number='234567',
            email='nikolaeva@mail.ru',
            registration_date=date(2023, 2, 10),
        ),
        Patient(
            last_name='Федоров',
            first_name='Михаил',
            patronymic='Александрович',
            birth_date=date(1978, 9, 3),
            gender='М',
            phone='+7 (921) 333-44-55',
            address='ул. Мира, д. 5, кв. 8',
            passport_series='4503',
            passport_number='345678',
            email='fedorov@mail.ru',
            registration_date=date(2023, 3, 5),
        ),
        Patient(
            last_name='Александрова',
            first_name='Татьяна',
            patronymic='Игоревна',
            birth_date=date(1995, 12, 12),
            gender='Ж',
            phone='+7 (921) 444-55-66',
            address='ул. Пушкина, д. 15, кв. 3',
            passport_series='4504',
            passport_number='456789',
            email='alexandrova@mail.ru',
            registration_date=date(2023, 4, 20),
        ),
        Patient(
            last_name='Дмитриев',
            first_name='Сергей',
            patronymic='Владимирович',
            birth_date=date(2000, 4, 30),
            gender='М',
            phone='+7 (921) 555-66-77',
            address='ул. Гагарина, д. 8, кв. 15',
            passport_series='4505',
            passport_number='567890',
            email='dmitriev@mail.ru',
            registration_date=date(2023, 5, 12),
        ),
    ]
    
    for patient in patients:
        session.add(patient)
    session.commit()
    
    # 5. Создание услуг
    services = [
        Service(code='CONS', name='Консультация терапевта', description='Первичная консультация врача-терапевта', price=1500.0, duration_minutes=30),
        Service(code='CARD', name='Консультация кардиолога', description='Консультация врача-кардиолога', price=2000.0, duration_minutes=40),
        Service(code='NEUR', name='Консультация невролога', description='Консультация врача-невролога', price=1800.0, duration_minutes=45),
        Service(code='SURG', name='Консультация хирурга', description='Консультация врача-хирурга', price=2500.0, duration_minutes=50),
        Service(code='ANAL', name='Общий анализ крови', description='Забор и анализ крови', price=800.0, duration_minutes=15),
        Service(code='ECG', name='ЭКГ', description='Электрокардиограмма', price=1200.0, duration_minutes=20),
        Service(code='US', name='УЗИ брюшной полости', description='Ультразвуковое исследование', price=3000.0, duration_minutes=60),
    ]
    
    for service in services:
        session.add(service)
    session.commit()
    
    # 6. Создание диагнозов
    diagnoses = [
        Diagnosis(code='I10', name='Эссенциальная (первичная) гипертензия', description='Повышенное артериальное давление', category='Кардиология', is_chronic=True),
        Diagnosis(code='J06.9', name='Острая инфекция верхних дыхательных путей неуточненная', description='Простуда, ОРВИ', category='Терапия', is_chronic=False),
        Diagnosis(code='M54.5', name='Боль внизу спины', description='Боль в поясничном отделе позвоночника', category='Неврология', is_chronic=False),
        Diagnosis(code='E11.9', name='Инсулиннезависимый сахарный диабет без осложнений', description='Сахарный диабет 2 типа', category='Эндокринология', is_chronic=True),
        Diagnosis(code='K29.7', name='Гастрит неуточненный', description='Воспаление слизистой оболочки желудка', category='Гастроэнтерология', is_chronic=True),
    ]
    
    for diagnosis in diagnoses:
        session.add(diagnosis)
    session.commit()
    
    # 7. Создание расписания на ближайшую неделю
    from datetime import timedelta
    
    today = datetime.now().date()
    doctors = session.query(Employee).filter(Employee.position_id.in_([1, 2, 3, 4])).all()
    
    for i in range(7):  # На 7 дней вперед
        work_date = today + timedelta(days=i)
        
        for doctor in doctors:
            # Создаем 5 слотов в день для каждого врача
            for slot in range(5):
                start_hour = 9 + slot  # с 9:00 до 14:00
                schedule = Schedule(
                    employee_id=doctor.id,
                    work_date=work_date,
                    start_time=time(start_hour, 0),
                    end_time=time(start_hour + 1, 0),
                    cabinet_number=doctor.cabinet_number,
                    max_patients=1,
                    notes='',
                    created_at=datetime.now()
                )
                session.add(schedule)
    
    session.commit()
    
    # 8. Создание записей на прием
    appointments = []
    schedules = session.query(Schedule).filter(Schedule.work_date >= today).limit(10).all()
    
    for i, schedule in enumerate(schedules):
        if i < len(patients):
            appointment = Appointment(
                patient_id=patients[i].id,
                schedule_id=schedule.id,
                doctor_id=schedule.employee_id,
                appointment_date=schedule.work_date,
                appointment_time=schedule.start_time,
                status=AppointmentStatus.SCHEDULED,
                reason='Консультация',
                created_at=datetime.now()
            )
            appointments.append(appointment)
    
    for appointment in appointments:
        session.add(appointment)
    session.commit()
    
    # 9. Создание медицинских записей
    medical_records = []
    for i, appointment in enumerate(appointments[:5]):
        record = MedicalRecord(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            complaints='Головная боль, слабость' if i == 0 else 'Боль в спине' if i == 1 else 'Повышенное давление' if i == 2 else 'Кашель, температура' if i == 3 else 'Боль в желудке',
            diagnosis_id=diagnoses[i % len(diagnoses)].id,
            examination_results='АД 140/90, ЧСС 80' if i == 0 else 'Ограничение подвижности позвоночника' if i == 1 else 'АД 160/100' if i == 2 else 'Хрипы в легких, температура 37.8' if i == 3 else 'Болезненность при пальпации',
            recommendations='Принимать препараты от давления, контроль через неделю' if i == 0 else 'Физиотерапия, ЛФК' if i == 1 else 'Гипотензивные препараты, диета' if i == 2 else 'Противовирусные препараты, постельный режим' if i == 3 else 'Диета, антациды',
            record_date=datetime.now(),
            next_visit_date=today + timedelta(days=14),
            is_emergency=(i == 2)
        )
        medical_records.append(record)
    
    for record in medical_records:
        session.add(record)
    session.commit()
    
    # 10. Создание назначений
    for i, record in enumerate(medical_records):
        prescription = Prescription(
            medical_record_id=record.id,
            medication_name='Эналаприл' if i == 0 else 'Диклофенак' if i == 1 else 'Амлодипин' if i == 2 else 'Арбидол' if i == 3 else 'Омепразол',
            dosage='10 мг' if i == 0 else '50 мг' if i == 1 else '5 мг' if i == 2 else '200 мг' if i == 3 else '20 мг',
            frequency='2 раза в день' if i == 0 else '3 раза в день' if i == 1 else '1 раз в день' if i == 2 else '4 раза в день' if i == 3 else '2 раза в день',
            duration='30 дней' if i == 0 else '10 дней' if i == 1 else '30 дней' if i == 2 else '7 дней' if i == 3 else '14 дней',
            instructions='Принимать утром и вечером' if i == 0 else 'После еды' if i == 1 else 'Утром' if i == 2 else 'До еды' if i == 3 else 'За 30 минут до еды',
            start_date=today,
            end_date=today + timedelta(days=30 if i == 0 else 10 if i == 1 else 30 if i == 2 else 7 if i == 3 else 14),
            is_completed=False
        )
        session.add(prescription)
    
    session.commit()
    
    print("База данных заполнена тестовыми данными!")
    print(f"- Должностей: {len(positions)}")
    print(f"- Специализаций: {len(specializations)}")
    print(f"- Сотрудников: {len(employees)}")
    print(f"- Пациентов: {len(patients)}")
    print(f"- Услуг: {len(services)}")
    print(f"- Диагнозов: {len(diagnoses)}")
    print(f"- Расписаний: {7 * len(doctors) * 5}")  # 7 дней * врачей * 5 слотов
    print(f"- Записей на прием: {len(appointments)}")
    print(f"- Медицинских записей: {len(medical_records)}")
    print(f"- Назначений: {len(medical_records)}")
    
    return True

def create_test_users(auth_manager):
    """Создание тестовых пользователей"""
    users = [
        ('admin', 'admin123', 'admin', 'admin@clinic.ru', None, None),
        ('doctor1', 'doctor123', 'doctor', 'ivanov@clinic.ru', 1, None),  # Связано с сотрудником ID 1
        ('doctor2', 'doctor123', 'doctor', 'petrova@clinic.ru', 2, None),  # Связано с сотрудником ID 2
        ('registrar', 'registrar123', 'registrar', 'smirnova@clinic.ru', 5, None),  # Связано с сотрудником ID 5
        ('patient1', 'patient123', 'patient', 'vasiliev@mail.ru', None, 1),  # Связано с пациентом ID 1
        ('patient2', 'patient123', 'patient', 'nikolaeva@mail.ru', None, 2),  # Связано с пациентом ID 2
    ]
    
    for username, password, role, email, employee_id, patient_id in users:
        success, message = auth_manager.register_user(username, password, role, email, employee_id, patient_id)
        if success:
            print(f"Создан пользователь: {username} ({role})")
        else:
            print(f"Ошибка создания пользователя {username}: {message}")