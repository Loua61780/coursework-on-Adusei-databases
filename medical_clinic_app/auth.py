from werkzeug.security import generate_password_hash, check_password_hash
from models import User, UserRole, Employee, Patient
from database import DatabaseManager
from datetime import datetime

class AuthManager:
    """Менеджер аутентификации и авторизации"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_user = None
    
    def register_user(self, username, password, role, email=None, employee_id=None, patient_id=None):
        """Регистрация нового пользователя"""
        session = self.db_manager.get_session()
        try:
            # Проверка существования пользователя
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                return False, "Пользователь с таким именем уже существует"
            
            # Проверка роли
            try:
                user_role = UserRole(role)
            except ValueError:
                return False, f"Недопустимая роль. Допустимые роли: {', '.join([r.value for r in UserRole])}"
            
            # Создание пользователя
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role=user_role,
                email=email,
                employee_id=employee_id,
                patient_id=patient_id,
                created_at=datetime.now(),
                is_active=True
            )
            
            session.add(new_user)
            session.commit()
            
            return True, "Пользователь успешно зарегистрирован"
        except Exception as e:
            session.rollback()
            return False, f"Ошибка регистрации: {str(e)}"
        finally:
            self.db_manager.close_session(session)
    
    def login(self, username, password):
        """Аутентификация пользователя"""
        session = self.db_manager.get_session()
        try:
            user = session.query(User).filter_by(username=username, is_active=True).first()
            
            if user and check_password_hash(user.password_hash, password):
                self.current_user = user
                
                # Получаем связанные данные в зависимости от роли
                if user.role == UserRole.DOCTOR and user.employee_id:
                    employee = session.query(Employee).filter_by(id=user.employee_id).first()
                    user_info = {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role.value,
                        'full_name': employee.full_name if employee else user.username,
                        'employee_id': user.employee_id
                    }
                elif user.role == UserRole.PATIENT and user.patient_id:
                    patient = session.query(Patient).filter_by(id=user.patient_id).first()
                    user_info = {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role.value,
                        'full_name': patient.full_name if patient else user.username,
                        'patient_id': user.patient_id
                    }
                else:
                    user_info = {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role.value,
                        'full_name': user.username
                    }
                
                return True, "Вход выполнен успешно", user_info
            else:
                return False, "Неверное имя пользователя или пароль", None
        except Exception as e:
            return False, f"Ошибка входа: {str(e)}", None
        finally:
            self.db_manager.close_session(session)
    
    def logout(self):
        """Выход из системы"""
        self.current_user = None
        return True, "Выход выполнен успешно"
    
    def get_current_user(self):
        """Получение текущего пользователя"""
        return self.current_user
    
    def has_permission(self, required_roles):
        """Проверка прав доступа"""
        if not self.current_user:
            return False
        
        if isinstance(required_roles, str):
            required_roles = [required_roles]
        
        return self.current_user.role.value in required_roles
    
    def create_default_admin(self):
        """Создание администратора по умолчанию"""
        session = self.db_manager.get_session()
        try:
            admin = session.query(User).filter_by(username='admin').first()
            if not admin:
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    role=UserRole.ADMIN,
                    email='admin@clinic.ru',
                    created_at=datetime.now(),
                    is_active=True
                )
                session.add(admin_user)
                session.commit()
                print("Создан администратор по умолчанию: admin / admin123")
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Ошибка создания администратора: {e}")
            return False
        finally:
            self.db_manager.close_session(session)