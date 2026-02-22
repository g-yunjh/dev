name = "yunjh"
age = 23

# 1. 문자열 보간 (String Interpolation) : #{ 변수 } 사용
puts "안녕! 나는 #{name}이고, 나이는 #{age}살이야."

# 2. 후치 if문 (Syntactic Sugar)
# 조건문이 한 줄일 때 뒤에 붙여서 영어 문장처럼 씁니다.
puts "성인입니다." if age >= 20

# 3. unless 문 (if not과 동일)
# "~가 아니라면"이라는 뜻으로, 부정 조건을 읽기 쉽게 만듭니다.
is_tired = false
puts "공부를 더 합시다!" unless is_tired

# 4. 괄호 생략 가능
# 메서드 호출 시 괄호를 생략해도 됩니다.
puts "괄호 없이도 출력이 됩니다"
