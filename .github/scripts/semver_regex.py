import os, re, sys

def main():
    tag = os.getenv("TAG")
    if tag is None:
        print('No tag provided')
        sys.exit(1)

    semver = re.compile(
        r"""
        ^(0|[1-9]\d*)\.
        (0|[1-9]\d*)\.
        (0|[1-9]\d*)
        (?:-
            (
                (?:0|[1-9]\d*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)
                (?:\.
                    (?:0|[1-9]\d*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)
                )*
            )
        )?
        (?:\+
            ([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)
        )?
        $
        """,
        re.VERBOSE,
    )

    gh_output_path = os.getenv('GITHUB_OUTPUT')
    if gh_output_path is None:
        print("GITHUB_OUTPUT env var is empty")
        sys.exit(1)
    
    print(f"GITHUB_OUTPUT: {gh_output_path}")
    if not semver.match(tag):
        print(f"Invalid SemVer: {tag}")
        with open(gh_output_path, "a") as f:
            f.write("valid=false")
        return 0

    print(f"Valid SemVer: {tag}")
    with open(gh_output_path, "a") as f:
        f.write("valid=true")

if __name__ == "__main__":
    main()
