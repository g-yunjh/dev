class Coffee
  # getter와 setter 메서드를 이 한 줄로 자동 생성합니다.
  attr_accessor :name, :price

  def initialize(name, price)
    @name = name   # @가 붙으면 인스턴스 변수입니다.
    @price = price
  end

  def info
    "#{@name}은 #{@price}원 입니다."
  end
end

# 객체 생성 (new 사용)
my_coffee = Coffee.new("아메리카노", 4500)

puts my_coffee.info        # => 아메리카노은 4500원 입니다.
my_coffee.price = 5000     # 가격 수정 (attr_accessor 덕분에 가능)
puts "가격 인상 후: #{my_coffee.price}"
