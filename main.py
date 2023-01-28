from app.Runner import Runner
import datetime

if __name__ == "__main__":

    try:
        print(datetime.datetime.now())
        Runner.run()
        print(datetime.datetime.now())
    except KeyboardInterrupt:
        pass
