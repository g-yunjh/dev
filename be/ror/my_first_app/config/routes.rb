Rails.application.routes.draw do
  root 'welcome#index' # 홈페이지

  get '/about', to: 'pages#about' # 소개 페이지
  get '/contact', to: 'pages#contact' # 연락처 페이지
  get '/posts', to: 'posts#index' # 게시글 목록 페이지
  get '/users', to: 'users#index' # 사용자 목록 페이지
end
