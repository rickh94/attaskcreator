"""Custom Exceptions for attaskcreator."""


class NoAttachmentError(Exception):
    """Exception for skipping attachments if something goes wrong instead of
    exiting the whole program.
    """
    pass
