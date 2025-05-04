import threading
import subprocess
from os import walk
from os.path import exists
from json import load, dump
from pandas import read_csv


class RunCmd(threading.Thread):
    stdin_text: str
    stdout_text: str | None = None
    execution_file_path: str

    def __init__(self, cmd: list[str], timeout: int, stdin_text: str,
                 execution_file_path: str) -> None:
        threading.Thread.__init__(self)

        self.cmd = cmd
        self.timeout = timeout
        self.stdin_text = stdin_text
        self.execution_file_path = execution_file_path

    def run(self):
        self.p = subprocess.Popen(
            self.execution_file_path,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )

        self.p.stdin.write(self.stdin_text + '\n')
        self.p.stdin.close()

        self.stdout_text = self.p.stdout.read()
        self.p.wait()

    def Run(self) -> str | None:
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.kill()
            self.join()
            return None
        return self.stdout_text


COLORS = {
    "black": 30,
    "red": 31,
    "yellow": 33,
    "green": 32,
    "white": 37
}

PROBLEM_NAMES_SET = {'A', 'B', 'C', 'D'}

CACHE_PATH = "./cache.json"


def reset_color() -> None:
    default_color = "\033[0m"
    print(default_color, end='')


def print_colored(text: str, color: str = "white", end="\n", sep=' ') -> None:
    color = "white" if color not in COLORS else color
    print(f"\033[{COLORS[color]}m{text}", end=end, sep=sep)
    reset_color()


def compile_file(cpp_program_path: str, compiler_path: str) -> str:
    """
    returns path to exe file
    """
    execution_file_name = "execution_file"
    compile_command = [
        compiler_path, cpp_program_path, "-o", execution_file_name
    ]

    subprocess.run(compile_command)
    return f"./{execution_file_name}"


def run_execution_file(execution_file_: str, stdin_text: str,
                       timeout: int) -> str | None:
    """
    returns out data or None in TL or exception case
    """
    try:
        return RunCmd([execution_file_],
                      timeout, stdin_text, execution_file_).Run()
    except Exception:
        return None


def check_answer(program_answer: str, expected_answer: str) -> bool:
    return program_answer.strip().split() == expected_answer.strip().split()


def check_program(problem_name: str, program_path: str) -> dict:
    """
    returns percentage of accepted tests
    """
    tests_path = f"./problems/{problem_name}/tests"
    files_list: list[str] = [*walk(tests_path)][0][2]
    files_pairs: list[tuple[str]] = [(files_list[index], files_list[index + 1])
                                     for index in range(0, len(files_list), 2)]

    counter_accepted_tests = 0
    amount_tests = len(files_pairs)

    response: dict[str, float | dict[int, str]] = {}
    response["tests"]: dict[int, str] = {}  # type: ignore

    test_id = 1

    df = read_csv("problems_time_limits.csv", sep=' ')
    timeout = int(df.at[0, problem_name])

    for test_file_path, answer_file_path in files_pairs:
        test_file = open(f"{tests_path}/{test_file_path}",
                         'r', encoding='utf-8')
        answer_file = open(
            f"{tests_path}/{answer_file_path}", 'r', encoding='utf-8')

        test = test_file.read()
        answer = answer_file.read()

        out = run_execution_file(program_path, test, timeout)
        if out is None:
            response["tests"][test_id] = "TL"
        elif not check_answer(out, answer):
            response["tests"][test_id] = "WA"
        else:
            response["tests"][test_id] = "AC"
            counter_accepted_tests += 1

        test_file.close()
        answer_file.close()

        test_id += 1

    response["percentage"] = counter_accepted_tests / amount_tests * 100
    return response


def update_cache(compiler_path: str = None,
                 last_problem_name: str = None,
                 program_path: str = None):

    with open(CACHE_PATH, 'w') as json_file:
        data = {
            "compiler_path": compiler_path,
            "program_path": program_path,
            "last_problem_name": last_problem_name
        }
        dump(data, json_file, indent=4)


def clear_cache() -> None:
    update_cache(None, None, None)


def main() -> None:
    # clear_cache()
    with open(CACHE_PATH, 'r', encoding="utf-8") as cache_file:
        cache = load(cache_file)

    problem_name = cache["last_problem_name"]
    cpp_program_path = cache["program_path"]
    compiler_path = cache["compiler_path"]

    if compiler_path is None:
        compiler_path = input("Enter compiler path: ")
        if not exists(compiler_path):
            print_colored("No such compiler file", "yellow")
            return

    if problem_name is None:
        problem_name = input("Enter problem name: ")
    else:
        want_change_last_problem_name = input(
            f"Last time you sent problem \"{problem_name}\".\n"
            "Would you like to change problem name? (y \\ n): "
        )
        if want_change_last_problem_name.lower() == 'y':
            problem_name = input("Enter problem name: ")

    if problem_name not in PROBLEM_NAMES_SET:
        print_colored("No such problem", "yellow")
        return

    if cpp_program_path is None or not exists(cpp_program_path):
        cpp_program_path: str = input("Enter full path to your cpp file: ")
        if not exists(cpp_program_path):
            print_colored("No such cpp file", "yellow")
            return

    update_cache(compiler_path, problem_name, cpp_program_path)

    execution_file_path = compile_file(cpp_program_path, compiler_path)

    checker_response = check_program(problem_name, execution_file_path)
    sep_line = '-' * 8

    for test_id, verdict in checker_response["tests"].items():
        color = "red" if (verdict != "AC") else "green"
        print_colored(f"{test_id}:  {verdict}", color=color)

        if test_id < len(checker_response["tests"]):
            print(sep_line)
        else:
            print("\n")

    percentage_accepted_tests = checker_response["percentage"]
    color = "green" if (percentage_accepted_tests == 100) else "red"

    print_colored(f"Your score: {round(percentage_accepted_tests)}%", color)


if __name__ == "__main__":
    main()
