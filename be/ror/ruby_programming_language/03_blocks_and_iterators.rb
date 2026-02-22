fruits = ["사과", "바나나", "체리"]

# 1. each 반복기
# 배열의 요소를 하나씩 꺼내서 |fruit| 파이프 안에 담고 실행합니다.
fruits.each do |fruit|
  puts "나는 #{fruit}를 좋아해!"
end

# 2. map (데이터 변환)
# 배열의 모든 요소를 변형해서 새로운 배열을 만듭니다.
# 블록 안의 코드가 한 줄일 때는 중괄호 { }를 주로 씁니다.
upper_fruits = fruits.map { |f| f.upcase }

p upper_fruits # => ["사과", "바나나", "체리"] (한글이라 변화 없으나 영문이면 대문자화 됨)

# 3. select (조건 필터링)
numbers = [1, 2, 3, 4, 5, 6]
evens = numbers.select { |n| n.even? } # 짝수만 골라내기

p evens # => [2, 4, 6]
