import math
import logging

def is_prime(n):
    if n == 2:
        return True

    lb = int(math.sqrt(n))

    ub = lb + 1
    logging.debug(f"lower sqrt:{lb}, upper sqrt:{ub}")
    for x in range(ub, n-1):
        y = math.sqrt(x**2-n)
        logging.debug(f"x={x}, y={y}")
        if y % 1 == 0:
            y = int(y)
            if x+y == n or x-y == n:
                continue
            logging.debug(f"y is a whole number, so the factors of {n} are {(x+y, x-y)}")
            return False
    
    return True