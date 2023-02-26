from app.Runner import Runner

if __name__ == "__main__":
    try:
        Runner.run_from_config()
    except KeyboardInterrupt:
        Runner.stop()