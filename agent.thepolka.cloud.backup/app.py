#!/usr/bin/env python3
"""Command line entry point for the Barbie agent platform."""
from __future__ import annotations
import argparse
from agents.security_agent import SecurityBarbie
from dashboard.app import serve

def main() -> None:
    parser = argparse.ArgumentParser(description="Polka Barbie agents")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="run safe security checks")
    scan.add_argument("--target", required=True, help="URL within ALLOWED_TARGETS")
    sub.add_parser("daily", help="scan every configured target")
    report = sub.add_parser("report", help="regenerate an HTML report from run id")
    report.add_argument("--run", type=int, required=True)
    server = sub.add_parser("serve", help="serve the local dashboard")
    server.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    if args.command == "serve": serve(args.port)
    else:
        agent = SecurityBarbie()
        if args.command == "scan":
            result = agent.run(args.target); print(f"Run {result.run_id}: {result.status}. Report: {result.report_path}")
        elif args.command == "daily":
            for result in agent.run_daily(): print(f"Run {result.run_id}: {result.target} — {result.status}")
        else: print(agent.regenerate_report(args.run))
if __name__ == "__main__": main()
