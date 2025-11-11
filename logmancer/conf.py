from django.conf import settings

DEFAULTS = {
    "LOG_SENSITIVE_KEYS": ["password", "token", "authorization"],
    "ENABLE_MIDDLEWARE": True,
    "AUTO_LOG_EXCEPTIONS": False,
    "CLEANUP_AFTER_DAYS": 30,
    "SIGNAL_EXCLUDE_MODELS": ["logmancer.LogEntry", "admin.LogEntry"],
    "PATH_EXCLUDE_PREFIXES": [],
    "DEFAULT_LOG_LEVEL": "INFO",
    "NOTIFICATIONS": {},
    "ENABLE_NOTIFICATIONS": False,
}


def get(key):
    """Get value from LOGMANCER settings"""
    logmancer_settings = getattr(settings, "LOGMANCER", {})
    if key in logmancer_settings:
        return logmancer_settings[key]
    return DEFAULTS.get(key)


def get_list(key):
    """Get list value from LOGMANCER settings"""
    val = get(key)
    if isinstance(val, (list, tuple)):
        return list(val)
    return []


def get_dict(key):
    """Get dictionary value from LOGMANCER settings"""
    val = get(key)
    if isinstance(val, dict):
        return val
    return DEFAULTS.get(key, {})


def get_bool(key):
    """Get boolean value from LOGMANCER settings"""
    val = get(key)
    if isinstance(val, bool):
        return val
    return DEFAULTS.get(key)


def get_int(key):
    """Get integer value from LOGMANCER settings"""
    val = get(key)
    if isinstance(val, int):
        return val
    return DEFAULTS.get(key, 0)


def should_exclude_model(model):
    """
    Determines whether the model should be excluded from signal logging.
    """
    ex_models = DEFAULTS["SIGNAL_EXCLUDE_MODELS"]
    exclude_list = ex_models + get_list("SIGNAL_EXCLUDE_MODELS")
    model_key = f"{model._meta.app_label}.{model.__name__}".lower()

    normalized_excludes = [m.lower() for m in exclude_list]

    return model_key in normalized_excludes


def should_exclude_path(path: str) -> bool:
    """
    Checks whether logging should be excluded for a given path in middleware.
    """
    prefixes = get_list("PATH_EXCLUDE_PREFIXES")
    return any(path.startswith(p) for p in prefixes)
