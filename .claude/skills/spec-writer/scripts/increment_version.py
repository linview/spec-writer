#!/usr/bin/env python3
"""根据变更类型递增语义化版本号。

用法：
  python3 increment_version.py 1.2.3 --type MAJOR   → 2.0.0
  python3 increment_version.py 1.2.3 --type MINOR   → 1.3.0
  python3 increment_version.py 1.2.3 --type PATCH   → 1.2.4
"""

import argparse
import sys


def increment_version(current: str, change_type: str) -> str:
    parts = current.split(".")
    if len(parts) != 3:
        print(f"错误：版本号格式不正确 '{current}'，期望 X.Y.Z", file=sys.stderr)
        sys.exit(1)

    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if change_type == "MAJOR":
        major += 1
        minor = 0
        patch = 0
    elif change_type == "MINOR":
        minor += 1
        patch = 0
    elif change_type == "PATCH":
        patch += 1
    else:
        print(f"错误：未知变更类型 '{change_type}'，期望 MAJOR/MINOR/PATCH", file=sys.stderr)
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def main():
    parser = argparse.ArgumentParser(description="递增语义化版本号")
    parser.add_argument("version", help="当前版本号 (如 1.2.3)")
    parser.add_argument("--type", required=True, choices=["MAJOR", "MINOR", "PATCH"],
                        help="变更类型")
    args = parser.parse_args()

    new_version = increment_version(args.version, args.type)
    print(new_version)


if __name__ == "__main__":
    main()
