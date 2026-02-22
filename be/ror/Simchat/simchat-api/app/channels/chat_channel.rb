class ChatChannel < ApplicationCable::Channel
  def subscribed
    # params[:room_id]는 프론트에서 보내줄 예정
    stream_from "chat_#{params[:room_id]}"
  end

  def unsubscribed
    stop_all_streams
  end
end
