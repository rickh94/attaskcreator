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
