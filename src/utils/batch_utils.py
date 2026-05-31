from itertools import islice


def batched(iterable, size):
    iterator = iter(iterable)

    while True:
        batch = list(islice(iterator, size))
    
        if not batch:
            break
    
        yield batch
