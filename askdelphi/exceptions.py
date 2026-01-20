"""Custom exceptions for AskDelphi integration."""


class AskDelphiError(Exception):
    """Base exception for AskDelphi-related errors."""
    pass


class AskDelphiAuthError(AskDelphiError):
    """Raised when authentication or session handling fails."""
    pass


class AskDelphiNotFoundError(AskDelphiError):
    """Raised when a requested resource is not found."""
    pass


class AskDelphiConflictError(AskDelphiError):
    """Raised when a conflict occurs (e.g. duplicate ID)."""
    pass
