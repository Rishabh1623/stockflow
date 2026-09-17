class NotFoundError(Exception):
    """Raised when a referenced entity (warehouse, order, item) doesn't exist."""


class InvalidTransitionError(Exception):
    """Raised when an order status change isn't allowed from its current state."""


class InsufficientStockError(Exception):
    """Raised when fulfilling an order would drive quantity_on_hand negative."""
