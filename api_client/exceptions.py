"""Aangepaste uitzonderingen voor AskDelphi integratie."""


class AskDelphiError(Exception):
    """Basisuitzondering voor AskDelphi-gerelateerde fouten."""
    pass


class AskDelphiAuthError(AskDelphiError):
    """Wordt gegenereerd wanneer authenticatie of sessiebeheer mislukt."""
    pass


class AskDelphiNotFoundError(AskDelphiError):
    """Wordt gegenereerd wanneer een aangevraagde resource niet wordt gevonden."""
    pass


class AskDelphiConflictError(AskDelphiError):
    """Wordt gegenereerd wanneer een conflict optreedt (bijv. dubbele ID)."""
    pass
