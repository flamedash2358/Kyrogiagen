from logging import Filter


class MaxLevelFilter(Filter):
    """
    Permits messages up to the specified log level
    """

    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return (
            record.levelno < self.level
        )  # "<" instead of "<=": since logger.setLevel is inclusive, this should be exclusive
