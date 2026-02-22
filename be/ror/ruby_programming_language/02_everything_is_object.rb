# 1. 숫자도 객체입니다.
# 5번 반복하라는 명령을 숫자 객체에게 직접 내립니다.
5.times do
  print "Ruby! "
end
puts "" # 줄바꿈

# 2. nil(없음)도 객체입니다.
puts nil.nil?  # => true (nil인지 물어보는 메서드)

# 3. 메서드 체이닝 (Method Chaining)
# 기차처럼 메서드를 연결해서 직관적인 데이터 처리가 가능합니다.
# "  hello  " -> 공백제거 -> 대문자로 -> 뒤집기
result = "  hello  ".strip.upcase.reverse
puts result  # => "OLLEH"
