import sys
from parser import Parser


def main() -> None:
    """Entry point for the Fly-in drone simulation."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>", file=sys.stderr)
        sys.exit(1)

    try:
        parser = Parser(sys.argv[1])
        graph = parser.parse()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()