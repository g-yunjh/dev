class MessagesController < ApplicationController
  before_action :set_message, only: %i[ show update destroy ]

  # GET /messages
  def index
    # room_id 파라미터가 있으면 그것만, 없으면 전부 다
    if params[:room_id].present?
      @messages = Message.where(room_id: params[:room_id])
    else
      @messages = Message.all
    end

    render json: @messages
  end

  # GET /messages/1
  def show
    render json: @message
  end

  # POST /messages
  def create
    @message = Message.new(message_params)

    if @message.save
      # 여기서 방송! (DB 저장 후 -> 소켓 전송)
      ActionCable.server.broadcast("chat_#{@message.room_id}", @message)
      render json: @message, status: :created
    else
      render json: @message.errors, status: :unprocessable_entity
    end
  end

  # PATCH/PUT /messages/1
  def update
    if @message.update(message_params)
      render json: @message
    else
      render json: @message.errors, status: :unprocessable_content
    end
  end

  # DELETE /messages/1
  def destroy
    @message.destroy!
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_message
      @message = Message.find(params.expect(:id))
    end

    # Only allow a list of trusted parameters through.
    def message_params
      params.expect(message: [ :content, :room_id, :username ])
    end
end
