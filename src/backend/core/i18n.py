"""
Internationalization (i18n) for authentication error messages.
Supports: Uzbek (uz), Russian (ru), English (en)
"""

ERROR_MESSAGES = {
    'uz': {
        
        'invalid_credentials': "Email yoki parol noto'g'ri.",
        'email_not_verified': "Email tasdiqlanmagan. Pochta qutingizni tekshiring.",
        'account_blocked': "Hisob bloklangan. Administrator bilan bog'laning.",
        'account_locked': "Hisob vaqtincha bloklangan (5 marta noto'g'ri parol). {minutes} daqiqadan keyin qayta urinib ko'ring.",

        
        'register_failed': "Ro'yxatdan o'tish muvaffaqiyatsiz. Ma'lumotlarni tekshiring.",
        'email_already_registered': "Bu email allaqachon ro'yxatdan o'tgan va tasdiqlangan.",
        'invalid_email_format': "Email formati noto'g'ri. To'g'ri email kiriting (misol: user@example.com).",
        'field_required': "Ushbu maydonni to'ldirish majburiy.",

        
        'first_name_invalid': "Ism noto'g'ri kiritildi. Faqat harflardan iborat bo'lishi kerak.",
        'first_name_too_long': "Ism juda uzun. Kamida {max_length} ta belgidan oshmasligi kerak.",
        'last_name_invalid': "Familiya noto'g'ri kiritildi. Faqat harflardan iborat bo'lishi kerak.",
        'last_name_too_long': "Familiya juda uzun. Kamida {max_length} ta belgidan oshmasligi kerak.",

        
        'phone_already_registered': "Bu telefon raqami allaqachon ro'yxatdan o'tgan.",
        'invalid_phone_format': "Telefon raqami formati noto'g'ri. Xalqaro formatda kiriting (misol: +998901234567).",

        
        'password_too_weak': "Parol juda oddiy. Kamida 8 ta belgi, raqam va harf bo'lishi kerak.",
        'password_too_short': "Parol juda qisqa. Kamida {min_length} ta belgi bo'lishi kerak.",
        'password_too_common': "Bu parol juda oddiy. Boshqa parol tanlang.",
        'password_entirely_numeric': "Parol faqat raqamlardan iborat bo'lmasligi kerak.",
        'wrong_password': "Joriy parol noto'g'ri.",
        'passwords_do_not_match': "Parollar mos kelmadi. Iltimos, tekshirib qayta kiriting.",

        
        'permission_denied': "Sizda ushbu resursdan foydalanish huquqi yo'q.",
        'admin_access_required': "Admin huquqi talab qilinadi.",
        'mentor_access_required': "Mentor huquqi talab qilinadi.",
        'staff_access_required': "Xodimlar huquqi talab qilinadi.",
        'student_access_required': "Talaba huquqi talab qilinadi.",

        
        'ip_rate_limit': "Juda ko'p urinishlar. Biroz kutib qayta urinib ko'ring.",
        'rate_limited': "Iltimos, {seconds} soniya kuting.",

        
        'invalid_token': "Havola noto'g'ri yoki muddati tugagan.",
        'token_expired': "Token muddati tugagan.",
        'token_reuse': "Xavfsizlik xatosi aniqlandi. Barcha sessiyalar yopildi.",
        'already_verified': "Email allaqachon tasdiqlangan.",

        
        'account_unavailable': "Hisob mavjud emas.",

        
        'file_too_large': "Fayl hajmi juda katta. Maksimal ruxsat etilgan hajm: {max_size} MB.",
        'invalid_file_type': "Fayl formati ruxsat etilmagan. Faqat quyidagilarni yuklash mumkin: {allowed_types}.",
    },

    'ru': {
        
        'invalid_credentials': "Неверный email или пароль.",
        'email_not_verified': "Email не подтверждён. Проверьте почту.",
        'account_blocked': "Аккаунт заблокирован. Обратитесь к администратору.",
        'account_locked': "Аккаунт временно заблокирован (5 неверных попыток). Попробуйте через {minutes} минут.",

        
        'register_failed': "Регистрация не удалась. Проверьте данные.",
        'email_already_registered': "Этот email уже зарегистрирован и подтверждён.",
        'invalid_email_format': "Неверный формат email. Введите корректный адрес (например: user@example.com).",
        'field_required': "Это поле обязательно для заполнения.",

        
        'first_name_invalid': "Неверное имя. Оно должно состоять только из букв.",
        'first_name_too_long': "Имя слишком длинное. Максимум {max_length} символов.",
        'last_name_invalid': "Неверная фамилия. Она должна состоять только из букв.",
        'last_name_too_long': "Фамилия слишком длинная. Максимум {max_length} символов.",

        
        'phone_already_registered': "Этот номер телефона уже зарегистрирован.",
        'invalid_phone_format': "Неверный формат телефона. Используйте международный формат (например: +998901234567).",

        
        'password_too_weak': "Пароль слишком простой. Минимум 8 символов, буквы и цифры.",
        'password_too_short': "Пароль слишком короткий. Минимум {min_length} символов.",
        'password_too_common': "Этот пароль слишком простой. Выберите другой.",
        'password_entirely_numeric': "Пароль не может состоять только из цифр.",
        'wrong_password': "Текущий пароль неверен.",
        'passwords_do_not_match': "Пароли не совпадают.",

        
        'permission_denied': "У вас нет прав для доступа к этому ресурсу.",
        'admin_access_required': "Требуется доступ администратора.",
        'mentor_access_required': "Требуется доступ ментора.",
        'staff_access_required': "Требуется доступ сотрудника.",
        'student_access_required': "Требуется доступ студента.",

        
        'ip_rate_limit': "Слишком много попыток. Подождите немного.",
        'rate_limited': "Пожалуйста, подождите {seconds} секунд.",

        
        'invalid_token': "Ссылка неверна или истекла.",
        'token_expired': "Токен истёк.",
        'token_reuse': "Обнаружена угроза безопасности. Все сессии закрыты.",
        'already_verified': "Email уже подтверждён.",

        
        'account_unavailable': "Аккаунт недоступен.",

        
        'file_too_large': "Файл слишком большой. Максимально допустимый размер: {max_size} МБ.",
        'invalid_file_type': "Недопустимый формат файла. Разрешены только: {allowed_types}.",
    },

    'en': {
        
        'invalid_credentials': "Invalid email or password.",
        'email_not_verified': "Email not verified. Check your inbox.",
        'account_blocked': "Account is blocked. Contact administrator.",
        'account_locked': "Account temporarily locked (5 failed attempts). Try again in {minutes} minutes.",

        
        'register_failed': "Registration failed. Please check your details.",
        'email_already_registered': "This email is already registered and verified.",
        'invalid_email_format': "Invalid email format. Enter a valid address (e.g., user@example.com).",
        'field_required': "This field is required.",

        
        'first_name_invalid': "Invalid first name. It must contain letters only.",
        'first_name_too_long': "First name is too long. Maximum length is {max_length} characters.",
        'last_name_invalid': "Invalid last name. It must contain letters only.",
        'last_name_too_long': "Last name is too long. Maximum length is {max_length} characters.",

        
        'phone_already_registered': "This phone number is already registered.",
        'invalid_phone_format': "Invalid phone number format. Use international format (e.g., +998901234567).",

        
        'password_too_weak': "Password is too weak. Minimum 8 characters, letters and numbers.",
        'password_too_short': "Password is too short. Minimum {min_length} characters required.",
        'password_too_common': "This password is too common. Choose a different one.",
        'password_entirely_numeric': "Password cannot be entirely numeric.",
        'wrong_password': "Current password is incorrect.",
        'passwords_do_not_match': "Passwords do not match.",

        
        'permission_denied': "You do not have permission to access this resource.",
        'admin_access_required': "Admin access required.",
        'mentor_access_required': "Mentor access required.",
        'staff_access_required': "Staff access required.",
        'student_access_required': "Student access required.",

        
        'ip_rate_limit': "Too many attempts. Please wait.",
        'rate_limited': "Please wait {seconds} seconds.",

        
        'invalid_token': "Invalid or expired link.",
        'token_expired': "Token has expired.",
        'token_reuse': "Security threat detected. All sessions revoked.",
        'already_verified': "Email already verified.",

        
        'account_unavailable': "Account unavailable.",

        
        'file_too_large': "File is too large. Maximum allowed size is {max_size} MB.",
        'invalid_file_type': "Invalid file type. Allowed formats: {allowed_types}.",
    }
}


def get_error_message(code: str, lang: str = 'uz', **kwargs) -> str:
    """
    Get localized error message by code.
    """
    message = None

    for l in [lang, 'uz', 'en']:
        lang_dict = ERROR_MESSAGES.get(l)
        if lang_dict and code in lang_dict:
            message = lang_dict[code]
            break

    if message is None:
        return f"System error: {code}"

    try:
        return message.format(**kwargs)
    except (KeyError, ValueError, IndexError):
        return message


def get_language_from_request(request_or_header) -> str:
    """
    Универсальная функция определения языка.
    Принимает либо объект request, либо строку Accept-Language.

    Args:
        request_or_header: Django/DRF request объект ИЛИ строка Accept-Language

    Returns:
        Двухбуквенный код языка ('uz', 'ru', 'en')

    Examples:
        >>> get_language_from_request(request)  
        'uz'
        >>> get_language_from_request('ru-RU,ru;q=0.9')  
        'ru'
    """
    
    if isinstance(request_or_header, str):
        
        accept_language = request_or_header
    else:
        
        try:
            
            accept_language = request_or_header.headers.get('Accept-Language', '')
        except AttributeError:
            
            accept_language = request_or_header.META.get('HTTP_ACCEPT_LANGUAGE', '')

    if not accept_language:
        return 'uz'

    
    languages = accept_language.split(',')

    
    first_lang = languages[0].split(';')[0].strip()
    lang_code = first_lang[:2].lower()

    
    if lang_code in ERROR_MESSAGES:
        return lang_code

    
    return 'uz'


























