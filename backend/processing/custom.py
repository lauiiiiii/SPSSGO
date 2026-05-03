from .common import process_not_supported_message


def handle(df, variables, params):
    return df, process_not_supported_message()

