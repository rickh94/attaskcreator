"""Custom Exceptions for attaskcreator."""


class NoAttachmentError(Exception):
    """Exception for skipping attachments if something goes wrong instead of
    exiting the whole program.
    """
    pass


class NoRecordError(Exception):
    """Exception raised if a record is not found matching a search in a certain
    table.
    """
    pass


class ConfigError(Exception):
    """Exception raised if configuration is incorrect."""
    pass


class NoPhraseError(Exception):
    """Exception raised if the phrase is not found in the search text."""
    pass


class RegexFailedError(Exception):
    """Exception raised if the regex doesn't return anything even though the
    phrase was in the search text.
    """
    pass
