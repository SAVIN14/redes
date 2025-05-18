class Log:

    @staticmethod
    def log(msg: str) -> None:
        print(f"{msg}", flush=True)