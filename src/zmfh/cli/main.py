from __future__ import annotations

import argparse
from typing import Optional, Sequence

from zmfh.cli.doctor import cmd_doctor
from zmfh.cli.status_cmd import cmd_status
from zmfh.cli.policy_cmd import cmd_policy
from zmfh.cli.trace_cmd import cmd_trace
from zmfh.cli.selftest_cmd import cmd_selftest

from zmfh.cli_config import cmd_config_find, cmd_config_show, cmd_config_validate, cmd_init


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zmfh")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="Run diagnostics and print environment status")
    sub.add_parser("status", help="Print current runtime status")

    # policy
    p_pol = sub.add_parser("policy", help="policy ops")
    pol_sub = p_pol.add_subparsers(dest="policy_cmd", required=True)
    pol_sub.add_parser("show", help="show loaded policy")
    p_chk = pol_sub.add_parser("check", help="check a module decision")
    p_chk.add_argument("module", help="module fullname")
    p_val = pol_sub.add_parser("validate", help="validate policy file")
    p_val.add_argument("path", nargs="?", default=None)

    # trace
    p_tr = sub.add_parser("trace", help="trace ops")
    tr_sub = p_tr.add_subparsers(dest="trace_cmd", required=True)
    p_tail = tr_sub.add_parser("tail", help="tail recent trace events")
    p_tail.add_argument("--n", type=int, default=50)
    tr_sub.add_parser("clear", help="clear trace")

    # config/init
    p_cfg = sub.add_parser("config", help="config ops")
    cfg_sub = p_cfg.add_subparsers(dest="config_cmd", required=True)
    cfg_sub.add_parser("find", help="print discovered config path")
    cfg_sub.add_parser("show", help="print merged config")
    p_cval = cfg_sub.add_parser("validate", help="validate config file")
    p_cval.add_argument("path", nargs="?", default=None)
    sub.add_parser("init", help="write ./.zmfh templates")

    sub.add_parser("selftest", help="Run end-to-end smoke tests")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "doctor":
        return cmd_doctor()
    if args.cmd == "status":
        return cmd_status()

    if args.cmd == "policy":
        return cmd_policy(args)
    if args.cmd == "trace":
        return cmd_trace(args)

    if args.cmd == "config":
        if args.config_cmd == "find":
            return cmd_config_find()
        if args.config_cmd == "show":
            return cmd_config_show()
        if args.config_cmd == "validate":
            return cmd_config_validate(args.path)
        return 2

    if args.cmd == "init":
        return cmd_init()

    if args.cmd == "selftest":
        return cmd_selftest()

    return 2