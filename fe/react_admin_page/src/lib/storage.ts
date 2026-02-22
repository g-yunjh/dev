import { supabase } from './supabase'

export const storage = {
  getImageUrl(furnitureId: string, imagePath: string): string {
    const { data } = supabase.storage
      .from('furniture-images')
      .getPublicUrl(`${furnitureId}/${imagePath}`)
    
    return data.publicUrl
  },

  getContactAttachmentUrl(contactId: string, filePath: string): string {
    // filePath may already be a full path like `${contactId}/timestamp_filename`
    const relativePath = filePath.includes('/') ? filePath : `${contactId}/${filePath}`
    const { data } = supabase.storage
      .from('contact-attachments')
      .getPublicUrl(relativePath)
    
    return data.publicUrl
  },

  async downloadAttachment(contactId: string, filePath: string): Promise<Blob> {
    // Support both full relative path and filename-only
    const relativePath = filePath.includes('/') ? filePath : `${contactId}/${filePath}`
    const { data, error } = await supabase.storage
      .from('contact-attachments')
      .download(relativePath)

    if (error) {
      throw new Error(`Failed to download attachment: ${error.message}`)
    }

    return data
  }
}
