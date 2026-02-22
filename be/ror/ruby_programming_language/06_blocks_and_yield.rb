# 1. 메서드가 블록(Block)을 받아 실행하기
def my_timer
  puts ">> 타이머 시작"
  yield  # 여기에 'do...end' 사이의 코드가 들어와서 실행됨
  puts ">> 타이머 종료"
end

my_timer do
  puts "   (지금 복잡한 계산 중...)"
  sleep 1
end

# 2. 블록에 변수 넘겨주기 (파이프 |변수| 사용)
# 레일즈의 each 문이 작동하는 원리입니다.
def my_each(array)
  i = 0
  while i < array.length
    yield array[i] # 배열의 요소를 블록으로 던져줌
    i += 1
  end
end

fruits = ["사과", "배", "포도"]

my_each(fruits) do |fruit|
  puts "내가 먹은 과일: #{fruit}"
end
