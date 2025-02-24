import argparse


def ensure_uint(test_runs: str, min_value: int = 1):
    if not str(test_runs).isdigit():
        raise argparse.ArgumentTypeError("Must be an integer point number")
    elif int(test_runs) < min_value:
        raise argparse.ArgumentTypeError(f"Argument must be >= {min_value}")
    return int(test_runs)


def serde_speed_argparse():
    parser = argparse.ArgumentParser(description="AVRO Serde speed for different models")
    parser.add_argument(
        "--test-runs",
        dest="test_runs",
        type=ensure_uint,
        help=f"Number of test runs (default 100_000)",
        default=100_000,
    )
    parser.add_argument(
        "--schema",
        dest="schema",
        type=str,
        help=f"AVSC Schema file path, (default 'schemas/user-registered.avsc')",
        default="schemas/user-registered.avsc",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        help="Print verbose output",
        action="store_true",
    )
    parser.add_argument(
        "--chart",
        dest="chart",
        help="Generate matplotlib chart after test runs",
        action="store_true",
    )
    args = parser.parse_args()
    return args
