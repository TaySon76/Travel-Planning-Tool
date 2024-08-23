import random 

def generate_random_digits(n=6):
    return "".join(map(str, random.sample(range(0, 10), n)))

def generate_random_digits_large(n=10):
    return "".join(map(str, random.sample(range(0,10), n)))