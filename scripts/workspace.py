"""python scripts/workspace.py backup | restore ARCHIVE --destination DIR"""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.backup import create_backup, restore_backup
from backend.core import init_db

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("backup")
    r = sub.add_parser("restore")
    r.add_argument("archive")
    r.add_argument("--destination", required=True)
    args = p.parse_args()
    if args.command == "backup":
        init_db()
        print(create_backup())
    else:
        print(restore_backup(args.archive, args.destination))

if __name__ == "__main__":
    main()
