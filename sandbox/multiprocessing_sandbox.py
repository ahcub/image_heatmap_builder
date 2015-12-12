import time
from multiprocessing import Pool
from random import randint


def func(x):
    time.sleep(x)
    if x % 2:
        raise Exception('Error')
    return x

if __name__ == '__main__':

    tasks_pool = Pool()

    range_ = [randint(1, 10) for x in range(10)]
    print(range_)
    results = []
    for x in range_:
        results.append(tasks_pool.apply_async(func, (x, )))

    flag = True

    while flag:
        flag = False
        next_results = []
        for res in results:
            if res.ready():
                if res.successful():
                    print(res.get())
                else:
                    print(res, "failed")
            else:
                flag = True
                next_results.append(res)

        results = next_results

        time.sleep(1)
