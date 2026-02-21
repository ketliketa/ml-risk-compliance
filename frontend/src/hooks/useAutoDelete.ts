import { useEffect } from 'react';
import api from '../lib/api';

export function useAutoDeleteOnRefresh() {
  useEffect(() => {
    // Delete all documents when page is about to unload/refresh
    const handleBeforeUnload = async () => {
      try {
        const res = await api.get('/documents');
        const documents = res.data || [];
        
        // Delete all documents synchronously if possible
        // Note: async operations in beforeunload may not complete
        // So we use a flag in localStorage to trigger cleanup on next load
        if (documents.length > 0) {
          localStorage.setItem('delete_documents_on_load', 'true');
        }
      } catch (err) {
        // Ignore errors
      }
    };

    // Also check on page load if we need to delete
    const checkAndDelete = async () => {
      if (localStorage.getItem('delete_documents_on_load') === 'true') {
        try {
          const res = await api.get('/documents');
          const documents = res.data || [];
          
          for (const doc of documents) {
            try {
              await api.delete(`/documents/${doc.document_id}`);
            } catch (err) {
              // Ignore errors
            }
          }
          
          localStorage.removeItem('delete_documents_on_load');
        } catch (err) {
          // Ignore errors
        }
      }
    };

    // Check on mount
    checkAndDelete();

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);
}
