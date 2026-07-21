from __future__ import annotations

import argparse
import logging
import time

import schedule

from report import run_once


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run_loop(interval: int) -> None:
    """의존성 없는 단순 반복 실행"""
    while True:
        run_once()
        time.sleep(interval)


def run_schedule(interval: int) -> None:
    """schedule 라이브러리 기반 선언적 반복 실행"""
    schedule.every(interval).seconds.do(run_once)
    run_once()

    while True:
        schedule.run_pending()
        time.sleep(1)


def parse_args() -> argparse.Namespace:
    """CLI 인자 파싱"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="초 단위 반복 실행 간격. 0이면 1회 실행",
    )
    parser.add_argument(
        "--mode",
        choices=["loop", "schedule"],
        default="loop",
        help="반복 실행 방식",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.interval == 0:
        run_once()
        return 0

    logger.info("반복 실행 시작: mode=%s, interval=%s초", args.mode, args.interval)
    logger.info("중지: Ctrl+C")

    try:
        if args.mode == "schedule":
            run_schedule(args.interval)
        else:
            run_loop(args.interval)
    except KeyboardInterrupt:
        logger.info("반복 실행 종료")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
