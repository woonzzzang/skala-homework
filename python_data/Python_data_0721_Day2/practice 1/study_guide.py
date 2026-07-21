import csv
from collections import Counter, defaultdict
from functools import reduce
import tracemalloc

tracemalloc.start()

def read_logs(path):
    """한 줄씩 읽어 dict로 흘려보내는 제너레이터"""
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f) # 헤더를 키로 자동 인식
        for row in reader:
            yield row # return 이 아니라 yield -> 제너레이터 함수

# gen = read_logs('../../data/web_logs.csv')
# for _ in range(3):
#     print(next(gen))

# total = 0

# by_status = Counter()
# by_path = Counter()
# by_hour = Counter()
# by_ip = Counter()

# 제너레이터 객체로 쭉 돌면서 필요한 값들만 +1 
# for row in read_logs('../../data/web_logs.csv'):
#     total += 1
#     by_status[row['status']] += 1 # 지나갈 때 마다 1씩 누적
#     by_path[row['path']] += 1
#     by_ip[row['ip']] += 1
#     hour = row['timestamp'][11:13] # 'YYYY-MM-DD HH:MM:SS' -> HH
#     by_hour[hour] += 1



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

init = {
    'total': 0, 
    'status': Counter(),
    'path' : Counter(),
    'ip' : Counter(),
    'hour' : Counter(),
    'hour_status' : defaultdict(Counter),
    }

result = reduce(fold, read_logs('../../data/web_logs.csv'), init)
# print(result['total'])

# 5xx 비율 계산 - 체크포인트 맞추기 
err_5xx = sum(count for status, count in result['status'].items() if status.startswith('5'))
ratio = err_5xx / result['total'] * 100
# print(f'5xx: {err_5xx}건 ({ratio:.1f}%)') # ≈ 8% 가 나오면 성공 

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

# tracemalloc으로 메모리 비교하기
# readlines() 버전과 제너레이터 버전을 각각 감싸서 최대 메모리를 찍어보면, 수십MB vs 수십KB 라는 극적인 차이를 볼 수 있습니다.

current, peak = tracemalloc.get_traced_memory()
print(f'최대 메모리: {peak / 1024 / 1024:.2f} MB')
tracemalloc.stop()