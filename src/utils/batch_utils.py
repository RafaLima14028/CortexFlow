from itertools import islice


def batched(iterable, size):
    iterator = iter(iterable)

    while batch := list(islice(iterable, size)):
        yield batch
