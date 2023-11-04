from slither_core.exceptions import SlitherException


class ParsingError(SlitherException):
    pass


class VariableNotFound(SlitherException):
    pass
