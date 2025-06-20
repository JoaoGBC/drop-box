import React, { useEffect, useRef, useState } from 'react';
import './DropArea.css';


const fileTypeAccepted = (file, acceptTypes) => {
    const accept = acceptTypes.split(',').map(t => t.trim().toLowerCase());
    if (accept.length === 1 && accept[0] === '*'){
        return true;
    }
    return (
        accept.includes(file.type) || 
        accept.includes(`${file.type.split('/')}/*`) ||
        accept.includes(`.${[...file.name.split('.')].at(-1)}`)
    );
}

const DropArea = (
    {
        accept = '*',
        maxFiles = 50,
        maxSize = 200000,
        onFilesAccepted = () => {console.log('aceito')},
        onFilesRejected = () => {console.log('rejeitado')}
    }
) => {
    const fileInputRef = useRef();
    const [isDraggin, setIsDraggin] = useState(false);
    useEffect(() => {
        onFilesAccepted(selectedFiles)
    })
    const dragCounter = useRef(0);
    const handleClick = () => {
        fileInputRef.current.click();
    }
    const [selectedFiles, setSelectedFiles] = useState([])

    const handleFileSelected = (files) => {
        if (maxFiles != undefined) {
            if (files.length > maxFiles){
                onFilesRejected()
                return;
            }
        }
        if(!files.every(file => !(file.size > maxSize))){
            onFilesRejected()
            return;
        }
        if(!files.every(file => fileTypeAccepted(file, accept))){
            onFilesRejected();
            return;
        }

        
        setSelectedFiles(prev => {
            const newFiles = files.filter(file => !prev.some(f => f.name === file.name));
            return [...prev, ...newFiles];
        });
        
        
        return;
    }

    const handleFileInput = (event) => {
        const files = [...event.target.files]
        handleFileSelected(files)
    }

    const handleDragEnter = (event) => {
        event.preventDefault();
        dragCounter.current += 1;
        setIsDraggin(true);
        console.log(dragCounter)
    }
    
    const handleDragExit = (event) =>{
        event.preventDefault();
        dragCounter.current -= 1;
        if (dragCounter.current === 0) {
            setIsDraggin(false);
        }
        console.log(dragCounter)
    }

    const handleFileDrop = (event) => {
        event.preventDefault();
        const files = [...event.dataTransfer.files]
        handleFileSelected(files);
    }

    const attState = (prev, file) => {
        let a = prev.filter(f => f !== file)
        return a
    }

    const removeFile = (file, event) => {
        event.stopPropagation();

        setSelectedFiles(prev => attState(prev, file));
        
    }


    const renderFileList = (selectedFile) => {
        const fileTypeIcon = {
            'application/pdf': 'picture_as_pdf',
            'application/msword': 'description',
            'image/png': 'image',
            'image/jpeg': 'image',
            'video/mp4': 'movie',
            'application/zip': 'folder_zip',
            'default': 'insert_drive_file'
        };
        const icon = fileTypeIcon[selectedFile.type] || fileTypeIcon['default'];
        return (
            <div key={selectedFile.name} className="file-card">
                <button className="remove-btn" onClick={(event) => removeFile(selectedFile, event)}>×</button>
                <span className="material-symbols-outlined file-icon">{icon}</span>
                <span className="file-meta">
                    {
                        Math.round(selectedFile.size / 1024)
                    } KB
                </span>
                <span className="file-name">{selectedFile.name}</span>
            </div>
        )
    };

    return (
        <>
            <input type="file" style={{ display:'none'}} ref={fileInputRef} onChange={handleFileInput} accept={accept} multiple={maxFiles>1} />
            <div className={`drop-area ${isDraggin ? 'drag-over' : ''}`}
                onClick={handleClick}
                onDragOver={(event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    event.dataTransfer.dropEffect = 'copy';
                }}
                onDrop={(event) => {
                    event.preventDefault();
                    handleFileDrop(event)
                  }}
                onDragEnter={handleDragEnter} 
                onDragLeave={handleDragExit}
            >
                <div className="icon">
                    <span className="material-symbols-outlined">
                        backup
                    </span>
                </div>
                Arraste os arquivos aqui
                {(selectedFiles.length  > 0) ? <hr className="divider" /> : ''}
                <div className='file-list'>
                    {selectedFiles.map(file => renderFileList(file))}
                </div>
            </div>
        </>
    );
}

export default DropArea;

