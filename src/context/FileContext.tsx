"use client";
import type { ReactNode } from 'react';
import { createContext, useCallback, useContext, useRef, useState } from 'react';
interface FileContextType {
    uploadedFiles: FileList | null;
    setUploadedFiles: (files: FileList | null) => void;
    consumeFiles: () => FileList | null;
}
const FileContext = createContext<FileContextType | undefined>(undefined);
export const FileProvider = ({ children }: {
    children: ReactNode;
}) => {
    const [uploadedFiles, setUploadedFilesState] = useState<FileList | null>(null);
    const consumedRef = useRef(false);
    const setUploadedFiles = useCallback((files: FileList | null) => {
        console.log('[FileContext] Setting files:', files?.length || 0);
        setUploadedFilesState(files);
        consumedRef.current = false;
    }, []);
    const consumeFiles = useCallback(() => {
        if (consumedRef.current) {
            console.log('[FileContext] Files already consumed, returning null');
            return null;
        }
        if (!uploadedFiles) {
            console.log('[FileContext] No files to consume');
            return null;
        }
        console.log('[FileContext] Consuming files:', uploadedFiles.length);
        consumedRef.current = true;
        setTimeout(() => {
            setUploadedFilesState(null);
        }, 0);
        return uploadedFiles;
    }, [uploadedFiles]);
    return (<FileContext.Provider value={{ uploadedFiles, setUploadedFiles, consumeFiles }}>
      {children}
    </FileContext.Provider>);
};
export const useFileContext = () => {
    const context = useContext(FileContext);
    if (!context) {
        throw new Error('useFileContext must be used within a FileProvider');
    }
    return context;
};
