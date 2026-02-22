class CreateMessages < ActiveRecord::Migration[8.1]
  def change
    create_table :messages do |t|
      t.text :content
      t.references :room, null: false, foreign_key: true
      t.string :username

      t.timestamps
    end
  end
end
