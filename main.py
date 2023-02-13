from app.Runner import Runner
import time

if __name__ == "__main__":
    start = time.perf_counter()
    Runner.run()
    finish = time.perf_counter()
    print(finish - start)