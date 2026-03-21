import pickle


def load_config_from_bytes(data):
    return pickle.loads(data)


def evaluate_expression(expr):
    return eval(expr)
