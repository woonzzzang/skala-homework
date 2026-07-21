import csv
from collections import Counter, defaultdict
from functools import reduce
import tracemalloc


LOG_PATH = '../../data/web_logs.csv'


def read_logs(path):
    """한 줄씩 읽어 dict로 흘려보내는 제너레이터"""
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f) # 헤더를 키로 자동 인식
        for row in reader:
            yield row # return 이 아니라 yield -> 제너레이터 함수


def read_logs_readlines(path):
    """readlines()로 파일 전체를 메모리에 올린 뒤 dict로 흘려보내는 버전"""
    with open(path, newline='', encoding='utf-8') as f:
        lines = f.readlines() # 전체 파일을 한 번에 메모리에 올림
        reader = csv.DictReader(lines)
        for row in reader:
            yield row


# fold 패턴 - functools.reduce로 '누적'을 함수로
"""
'reduce'는 [앞의 결과 + 새 값 -> 새 결과]를 반복하는 도구
for문의 누적과 같은 일을 함수로 표현한 것
집계 로직을 재사용 가능한 함수로 만드는 사고 함양
"""
def fold(acc,row):
    """누적기(acc)에 row 하나를 반영해서 돌려준다"""
    acc['total'] += 1
    acc['status'][row['status']] += 1
    acc['path'][row['path']] += 1
    acc['ip'][row['ip']] += 1

    hour = row['timestamp'][11:13]
    acc['hour'][hour] += 1
    acc['hour_status'][hour][row['status']] += 1

    return acc


def make_init():
    """readlines 버전과 제너레이터 버전이 서로 다른 누적기를 쓰도록 새로 만든다"""
    return {
        'total': 0,
        'status': Counter(),
        'path' : Counter(),
        'ip' : Counter(),
        'hour' : Counter(),
        'hour_status' : defaultdict(Counter),
        }


def measure_memory(title, rows):
    """집계 코드 실행 중 최대 메모리 사용량을 측정한다"""
    tracemalloc.start()
    result = reduce(fold, rows, make_init())
    current, peak = tracemalloc.get_traced_memory()
    print(f'{title} 최대 메모리: {peak / 1024 / 1024:.2f} MB')
    tracemalloc.stop()

    return result


def print_report(result):
    """집계 결과를 체크포인트에 맞게 리포트로 출력한다"""
    # 5xx 비율 계산 - 체크포인트 맞추기
    err_5xx = sum(count for status, count in result['status'].items() if status.startswith('5'))
    ratio = err_5xx / result['total'] * 100

    # 리포트로 예쁘게 출력 + 상위 IP
    print('=' * 40)
    print(f"총 요청 수 : {result['total']:,}")
    print(f'5xx 오류율 : {ratio:.1f}%')
    print('-- 인기 경로 TOP 5 --')
    for path, cnt in result['path'].most_common(5):
        print(f' {path:<20} {cnt:>7,}')
    print('-- 시간대별 요청 수 --')
    for hour, cnt in result['hour'].most_common(5):
        print(f' {hour}시 {cnt:>23,}')
    print('-- 시간대별 상태코드 요청 수 TOP 5--')
    for hour in sorted(result['hour_status']):
        print(f' {hour}시')
        for status, cnt in result['hour_status'][hour].most_common(5):
            print(f' status={status:<13} {cnt:>7,}')
    print('-- 접속 상위 IP TOP 5 --')
    for ip, cnt in result['ip'].most_common(5):
        print(f' {ip:<20} {cnt:>7,}')


def main():
    # tracemalloc으로 메모리 비교하기
    # readlines() 버전과 제너레이터 버전을 각각 감싸서 최대 메모리를 찍어보면, 수십MB vs 수십KB 라는 극적인 차이를 볼 수 있습니다.
    print('=' * 40)
    print('-- 메모리 비교 --')

    readlines_result = measure_memory(
        'readlines() 버전',
        read_logs_readlines(LOG_PATH)
    )

    result = measure_memory(
        '제너레이터 버전',
        read_logs(LOG_PATH)
    )

    print_report(result)


if __name__ == "__main__":
    main()
