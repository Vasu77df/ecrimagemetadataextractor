# This file is exempted from test coverage
# do not put business logic in here

from sys import argv

from ecrimagemetadataextractor.cli import main


def runner() -> None:
    main(argv[1:])


if __name__ == "__main__":
    main(argv[1:])
