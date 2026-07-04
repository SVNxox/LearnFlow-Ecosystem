

**Date:** 2026-06-16  
**Status:** 🔴 CRITICAL ISSUES FOUND  
**Priority:** P0 — Блокирует пользователей

---



Проведён полный аудит системы аутентификации (backend + frontend). Найдено **8 критических проблем**, которые объясняют жалобы пользователя:

1. ❌ **Email reuse issue** — нельзя войти после регистрации с тем же email
2. ❌ **Unclear error messages** — сообщения на английском, непонятные
3. ❌ **Missing Uzbek localization** — нет локализации
4. ❌ **Poor error handling** — generic ошибки без деталей
5. ❌ **Email verification UX** — не ясно что делать после регистрации
6. ❌ **Password validation errors** — показываются на английском
7. ❌ **Account lockout confusion** — пользователь не понимает почему заблокирован
8. ❌ **Missing role assignment check** — crash если роль Student не существует

---





Пользователь регистрируется с email `user@example.com`, но НЕ верифицирует email. Затем пытается:
- Снова зарегистрироваться с тем же email → **Ошибка:** "Registration failed"
- Войти с тем же email → **Ошибка:** "Email not verified"

**Результат:** Email "застрял" — нельзя ни зарегистрироваться заново, ни войти.



```python

if User.objects.filter(email=email).exists():
    
    raise AuthError("Registration failed. Please check your details.", code="register_failed")
```

**Проблема:** Если пользователь зарегистрировался, но не верифицировал email, он не может ни войти (email not verified), ни зарегистрироваться заново (email exists).



**Вариант 1: Allow re-registration for unverified users (рекомендуется)**

```python
def register_user(email: str, password: str, first_name: str, last_name: str) -> User:
    email = email.lower().strip()

    existing_user = User.objects.filter(email=email).first()
    
    if existing_user:
        if existing_user.is_active:
            
            raise AuthError(
                "Bu email allaqachon ro'yxatdan o'tgan.", 
                code="email_already_registered"
            )
        else:
            
            
            existing_user.delete()
            
    
    
    user = User.objects.create_user(email=email, password=password)
    
```

**Вариант 2: Resend verification email**

Добавить кнопку "Resend verification email" на странице login с проверкой is_active.

---





Все ошибки на английском языке:
- "Invalid credentials"
- "Email not verified"
- "Registration failed"

Пользователь из Узбекистана НЕ понимает что произошло.



```python

raise AuthError("Invalid credentials.", code="invalid_credentials")
raise AuthError("Email not verified. Check your inbox.", code="email_not_verified")
raise AuthError("Account is suspended.", code="account_blocked")
raise AuthError("Registration failed. Please check your details.", code="register_failed")
```



**Создать файл с переводами:**

```python

ERROR_MESSAGES = {
    'uz': {
        'invalid_credentials': "Email yoki parol noto'g'ri.",
        'email_not_verified': "Email tasdiqlanmagan. Pochta qutingizni tekshiring.",
        'account_blocked': "Hisob bloklangan. Administrator bilan bog'laning.",
        'account_locked': "Hisob vaqtincha bloklangan. {time} dan keyin qayta urinib ko'ring.",
        'email_already_registered': "Bu email allaqachon ro'yxatdan o'tgan.",
        'register_failed': "Ro'yxatdan o'tish muvaffaqiyatsiz. Ma'lumotlarni tekshiring.",
        'password_too_weak': "Parol juda oddiy. Kamida 8 ta belgi, raqam va harf bo'lishi kerak.",
        'ip_rate_limit': "Juda ko'p urinishlar. Biroz kutib qayta urinib ko'ring.",
        'email_resend_cooldown': "Email qayta yuborish uchun {seconds} soniya kuting.",
    },
    'ru': {
        'invalid_credentials': "Неверный email или пароль.",
        'email_not_verified': "Email не подтверждён. Проверьте почту.",
        'account_blocked': "Аккаунт заблокирован. Обратитесь к администратору.",
        'account_locked': "Аккаунт временно заблокирован. Попробуйте после {time}.",
        'email_already_registered': "Этот email уже зарегистрирован.",
        'register_failed': "Регистрация не удалась. Проверьте данные.",
        'password_too_weak': "Пароль слишком простой. Минимум 8 символов, буквы и цифры.",
        'ip_rate_limit': "Слишком много попыток. Подождите немного.",
        'email_resend_cooldown': "Подождите {seconds} секунд перед повторной отправкой.",
    },
    'en': {
        'invalid_credentials': "Invalid email or password.",
        'email_not_verified': "Email not verified. Check your inbox.",
        'account_blocked': "Account is blocked. Contact administrator.",
        'account_locked': "Account temporarily locked. Try again after {time}.",
        'email_already_registered': "This email is already registered.",
        'register_failed': "Registration failed. Please check your details.",
        'password_too_weak': "Password is too weak. Minimum 8 characters, letters and numbers.",
        'ip_rate_limit': "Too many attempts. Please wait.",
        'email_resend_cooldown': "Wait {seconds} seconds before resending email.",
    }
}

def get_error_message(code: str, lang: str = 'uz', **kwargs) -> str:
    """Get localized error message."""
    messages = ERROR_MESSAGES.get(lang, ERROR_MESSAGES['en'])
    message = messages.get(code, ERROR_MESSAGES['en'].get(code, 'Unknown error'))
    return message.format(**kwargs)
```

**Обновить AuthError:**

```python
class AuthError(Exception):
    def __init__(self, code: str, lang: str = 'uz', **format_kwargs):
        self.code = code
        self.message = get_error_message(code, lang, **format_kwargs)
        super().__init__(self.message)
```

**Использование:**

```python

lang = request.headers.get('Accept-Language', 'uz')[:2]


raise AuthError('invalid_credentials', lang=lang)
raise AuthError('account_locked', lang=lang, time='15:30')
```

---





Backend не знает какой язык использовать. Frontend не отправляет `Accept-Language` header.



**Frontend — добавить header:**

```typescript
// src/frontend/src/lib/api-client.ts
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      // NEW: Add language header
      const lang = localStorage.getItem('language') || 'uz';
      config.headers['Accept-Language'] = lang;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

**Backend — читать header:**

```python

def post(self, request):
    serializer = LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    
    lang = request.headers.get('Accept-Language', 'uz')[:2]
    
    try:
        result = login_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            request=request,
            lang=lang,  
        )
    except AuthError as exc:
        return Response(
            {'error': exc.message, 'code': exc.code},
            status=status.HTTP_401_UNAUTHORIZED,
        )
```

---





Django password validators возвращают ошибки на английском:

```
"This password is too common."
"This password is entirely numeric."
"The password is too similar to the email address."
```



**Создать кастомные валидаторы с переводами:**

```python

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)

class UzbekMinimumLengthValidator(MinimumLengthValidator):
    def get_help_text(self):
        return f"Parol kamida {self.min_length} ta belgidan iborat bo'lishi kerak."
    
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                f"Parol juda qisqa. Kamida {self.min_length} ta belgi bo'lishi kerak.",
                code='password_too_short',
            )

class UzbekCommonPasswordValidator(CommonPasswordValidator):
    def get_help_text(self):
        return "Parol juda oddiy bo'lmasligi kerak."
    
    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                "Bu parol juda oddiy. Boshqa parol tanlang.",
                code='password_too_common',
            )

class UzbekNumericPasswordValidator(NumericPasswordValidator):
    def get_help_text(self):
        return "Parol faqat raqamlardan iborat bo'lmasligi kerak."
    
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                "Parol faqat raqamlardan iborat bo'lmasligi kerak.",
                code='password_entirely_numeric',
            )
```

**Обновить settings.py:**

```python
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "src.backend.identity.validators.UzbekMinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "src.backend.identity.validators.UzbekCommonPasswordValidator"},
    {"NAME": "src.backend.identity.validators.UzbekNumericPasswordValidator"},
]
```

---





После регистрации пользователь видит:

```
"Registration successful. Please verify your email."
```

Но НЕ понятно:
- Куда отправлен email?
- Что делать если email не пришёл?
- Как запросить повторную отправку?



**Улучшить страницу verify-email:**

```typescript
// src/frontend/src/app/(auth)/verify-email/page.tsx
export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const email = searchParams.get('email');
  const [resending, setResending] = useState(false);
  const [resent, setResent] = useState(false);
  const [error, setError] = useState('');

  const handleResend = async () => {
    if (!email) return;
    
    try {
      setResending(true);
      setError('');
      await api.auth.resendVerification(email);
      setResent(true);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow">
        <div className="text-center">
          <div className="text-6xl mb-4">📧</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Emailni tasdiqlang
          </h1>
          <p className="text-gray-600 mb-6">
            <strong>{email}</strong> manziliga tasdiqlash havolasi yuborildi.
          </p>
          
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-6 text-left">
            <p className="text-sm text-blue-800 mb-2">
              <strong>Keyingi qadamlar:</strong>
            </p>
            <ol className="text-sm text-blue-700 list-decimal list-inside space-y-1">
              <li>Pochta qutingizni oching</li>
              <li>LearnFlow'dan kelgan xabarni toping</li>
              <li>Tasdiqlash havolasini bosing</li>
            </ol>
          </div>

          {resent && (
            <div className="bg-green-50 border border-green-200 p-3 rounded mb-4">
              <p className="text-sm text-green-700">
                ✅ Email qayta yuborildi!
              </p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 p-3 rounded mb-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <button
            onClick={handleResend}
            disabled={resending || resent}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium disabled:opacity-50"
          >
            {resending ? 'Yuborilmoqda...' : resent ? 'Yuborildi ✓' : 'Emailni qayta yuboring'}
          </button>

          <div className="mt-6 pt-6 border-t">
            <p className="text-xs text-gray-500 mb-2">
              Email kelmadimi? Spam papkasini tekshiring.
            </p>
            <Link href="/login" className="text-sm text-blue-600 hover:text-blue-700">
              ← Kirish sahifasiga qaytish
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---





После 5 неудачных попыток аккаунт блокируется на 15 минут, но сообщение непонятное:

```
"Account locked. Try again after 15:30 UTC."
```

Пользователь не понимает:
- Почему заблокирован?
- Сколько осталось ждать?
- Как разблокировать?



**Улучшить сообщение:**

```python

if user.is_locked:
    remaining = user.locked_until - timezone.now()
    minutes = int(remaining.total_seconds() / 60)
    
    _record_attempt(False, "locked")
    
    raise AuthError(
        'account_locked',
        lang=lang,
        minutes=minutes,
    )


'account_locked': "Hisob vaqtincha bloklangan (5 marta noto'g'ri parol). {minutes} daqiqadan keyin qayta urinib ko'ring.",
```

**Показать на frontend:**

```typescript
// login/page.tsx
{error && (
  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
    <p className="font-medium mb-1">Kirish xatosi</p>
    <p>{error}</p>
    {error.includes('bloklangan') && (
      <p className="mt-2 text-xs">
        💡 Maslahat: Parolni unutdingizmi? 
        <Link href="/password-reset" className="underline ml-1">
          Parolni tiklash
        </Link>
      </p>
    )}
  </div>
)}
```

---





Если в базе нет роли "student", регистрация падает:

```python

student_role = Role.objects.get(name=Role.STUDENT)  
```



**Добавить проверку и создание роли:**

```python
def register_user(email: str, password: str, first_name: str, last_name: str, lang: str = 'uz') -> User:
    
    
    
    student_role, _ = Role.objects.get_or_create(
        name=Role.STUDENT,
        defaults={'description': 'Default student role'}
    )
    UserRole.objects.create(user=user, role=student_role)
    
    
```

**Создать migration для ролей:**

```python

from django.db import migrations

def create_default_roles(apps, schema_editor):
    Role = apps.get_model('identity', 'Role')
    
    roles = [
        ('student', 'Default student role'),
        ('mentor', 'Course mentor role'),
        ('staff', 'Staff member role'),
        ('admin', 'Administrator role'),
    ]
    
    for name, description in roles:
        Role.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('identity', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(create_default_roles),
    ]
```

---





Frontend показывает generic ошибки:

```typescript
setError(err instanceof Error ? err.message : 'Login failed');
```

Если backend возвращает structured error, frontend теряет детали.



**Улучшить handleApiError:**

```typescript
// src/frontend/src/lib/api-client.ts
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{
      error?: string;
      detail?: string;
      message?: string;
      code?: string;
      non_field_errors?: string[];
      email?: string[];
      password?: string[];
    }>;

    if (axiosError.response?.data) {
      const data = axiosError.response.data;
      
      // Priority 1: Explicit error field
      if (data.error) return data.error;
      
      // Priority 2: Detail field
      if (data.detail) return data.detail;
      
      // Priority 3: Field-specific errors
      if (data.email && Array.isArray(data.email)) {
        return `Email: ${data.email[0]}`;
      }
      if (data.password && Array.isArray(data.password)) {
        return `Parol: ${data.password[0]}`;
      }
      
      // Priority 4: Non-field errors
      if (data.non_field_errors?.[0]) {
        return data.non_field_errors[0];
      }
      
      // Priority 5: Message field
      if (data.message) return data.message;
    }

    // Network errors
    if (axiosError.message === 'Network Error') {
      return "Internet aloqasi yo'q. Iltimos, qayta urinib ko'ring.";
    }
    
    if (axiosError.code === 'ECONNABORTED') {
      return "So'rov juda uzoq davom etdi. Qayta urinib ko'ring.";
    }

    if (axiosError.message) return axiosError.message;
  }

  return "Kutilmagan xatolik yuz berdi.";
};
```

---





1. ✅ **Fix email reuse issue** (30 min)
   - Allow re-registration for unverified users
   
2. ✅ **Add Uzbek error messages** (1 hour)
   - Create i18n.py with translations
   - Update AuthError to use translations
   
3. ✅ **Add Accept-Language header** (30 min)
   - Frontend: api-client.ts
   - Backend: read header in views
   
4. ✅ **Fix missing role crash** (30 min)
   - Create migration for default roles
   - Use get_or_create in register_user



5. ✅ **Improve verify-email page** (30 min)
   - Better UX with resend button
   - Clear instructions in Uzbek

6. ✅ **Better error handling** (30 min)
   - Improve handleApiError
   - Show field-specific errors

7. ✅ **Account lockout improvements** (30 min)
   - Show remaining minutes
   - Link to password reset



8. ✅ **Custom password validators** (30 min)
   - Uzbek error messages
   
9. ✅ **Add language switcher** (30 min)
   - UI component
   - Store preference in localStorage

---



**Найдено:** 8 критических проблем  
**Estimated fix time:** 4-6 hours  
**Impact:** Разблокирует всех пользователей

**Root causes:**
1. Отсутствие локализации (все ошибки на английском)
2. Плохая обработка edge cases (unverified user re-registration)
3. Unclear UX (не ясно что делать после регистрации)
4. Missing data (роли не созданы при деплое)

**Next steps:**
1. Implement Phase 1 fixes (URGENT)
2. Test with real Uzbek users
3. Add language switcher
4. Improve email templates (тоже на Uzbek)
