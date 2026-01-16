from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, ForeignKey, Text, Float, Time, Enum, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from datetime import datetime

Base = declarative_base()

# Перечисление для ролей пользователей
class UserRole(enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    REGISTRAR = "registrar"
    PATIENT = "patient"

# Перечисление для статусов записи
class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

# 1. Сущность Пользователь (для аутентификации)
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    # Связи
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=True)

    employee = relationship("Employee", back_populates="user_account", uselist=False)
    patient = relationship("Patient", back_populates="user_account", uselist=False)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

# 2. Сущность Пациент
class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    patronymic = Column(String(100))
    birth_date = Column(Date, nullable=False)
    gender = Column(String(10))
    phone = Column(String(20))
    address = Column(String(200))
    passport_series = Column(String(10))
    passport_number = Column(String(20))
    email = Column(String(100))
    registration_date = Column(Date, default=datetime.now().date())
    
    # Связи
    user_account = relationship("User", back_populates="patient", uselist=False)
    medical_records = relationship("MedicalRecord", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    
    @hybrid_property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic or ''}".strip()
    
    @hybrid_property
    def age(self):
        if self.birth_date:
            today = datetime.now().date()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.full_name}')>"

# 3. Сущность Сотрудник
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    patronymic = Column(String(100))
    birth_date = Column(Date)
    phone = Column(String(20))
    email = Column(String(100))
    hire_date = Column(Date, default=datetime.now().date())
    cabinet_number = Column(String(10))
    
    # Внешние ключи
    position_id = Column(Integer, ForeignKey('positions.id'), nullable=False)
    specialization_id = Column(Integer, ForeignKey('specializations.id'), nullable=True)
    
    # Связи
    user_account = relationship("User", back_populates="employee", uselist=False)
    position = relationship("Position", back_populates="employees")
    specialization = relationship("Specialization", back_populates="employees")
    schedules = relationship("Schedule", back_populates="employee")
    medical_records = relationship("MedicalRecord", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    
    @hybrid_property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic or ''}".strip()
    
    @hybrid_property
    def full_title(self):
        spec = self.specialization.name if self.specialization else ""
        return f"{self.position.name} {spec} {self.full_name}".strip()
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.full_name}', position='{self.position.name if self.position else None}')>"

# 4. Сущность Должность
class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    min_salary = Column(Float)
    max_salary = Column(Float)
    
    # Связи
    employees = relationship("Employee", back_populates="position")
    
    def __repr__(self):
        return f"<Position(id={self.id}, name='{self.name}')>"

# 5. Сущность Специализация
class Specialization(Base):
    __tablename__ = 'specializations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))  # терапевтическая, хирургическая и т.д.
    
    # Связи
    employees = relationship("Employee", back_populates="specialization")
    
    def __repr__(self):
        return f"<Specialization(id={self.id}, name='{self.name}')>"

# 6. Сущность Расписание
class Schedule(Base):
    __tablename__ = 'schedules'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    work_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    cabinet_number = Column(String(10))
    max_patients = Column(Integer, default=1)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Связи
    employee = relationship("Employee", back_populates="schedules")
    appointments = relationship("Appointment", back_populates="schedule")
    
    @hybrid_property
    def available_slots(self):
        if self.appointments:
            return self.max_patients - len([a for a in self.appointments if a.status == AppointmentStatus.SCHEDULED])
        return self.max_patients
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, doctor={self.employee.full_name if self.employee else None}, date={self.work_date})>"

# 7. Сущность Запись на прием
class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('schedules.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Связи
    patient = relationship("Patient", back_populates="appointments")
    schedule = relationship("Schedule", back_populates="appointments")
    doctor = relationship("Employee", back_populates="appointments")
    medical_record = relationship("MedicalRecord", back_populates="appointment", uselist=False)
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient='{self.patient.full_name if self.patient else None}', date={self.appointment_date})>"

# 8. Сущность Медицинская карта
class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    complaints = Column(Text)
    diagnosis_id = Column(Integer, ForeignKey('diagnoses.id'), nullable=True)
    examination_results = Column(Text)
    recommendations = Column(Text)
    record_date = Column(DateTime, default=datetime.now)
    next_visit_date = Column(Date)
    is_emergency = Column(Boolean, default=False)
    
    # Связи
    appointment = relationship("Appointment", back_populates="medical_record")
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Employee", back_populates="medical_records")
    diagnosis = relationship("Diagnosis", back_populates="medical_records")
    prescriptions = relationship("Prescription", back_populates="medical_record")
    
    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, patient='{self.patient.full_name if self.patient else None}', date={self.record_date})>"

# 9. Сущность Диагноз
class Diagnosis(Base):
    __tablename__ = 'diagnoses'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)  # МКБ-10 код
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    is_chronic = Column(Boolean, default=False)
    
    # Связи
    medical_records = relationship("MedicalRecord", back_populates="diagnosis")
    
    def __repr__(self):
        return f"<Diagnosis(id={self.id}, code='{self.code}', name='{self.name}')>"

# 10. Сущность Назначение
class Prescription(Base):
    __tablename__ = 'prescriptions'
    
    id = Column(Integer, primary_key=True)
    medical_record_id = Column(Integer, ForeignKey('medical_records.id'), nullable=False)
    medication_name = Column(String(200), nullable=False)
    dosage = Column(String(100))
    frequency = Column(String(100))
    duration = Column(String(50))
    instructions = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    is_completed = Column(Boolean, default=False)
    
    # Связи
    medical_record = relationship("MedicalRecord", back_populates="prescriptions")
    
    def __repr__(self):
        return f"<Prescription(id={self.id}, medication='{self.medication_name}')>"

# 11. Сущность Услуга
class Service(Base):
    __tablename__ = 'services'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, default=30)
    category = Column(String(100))
    is_available = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}', price={self.price})>"