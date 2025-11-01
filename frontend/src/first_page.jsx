import { useState } from "react"
import { useNavigate } from "react-router-dom";

export default function FirstPage(){
    const [images, setImages] = useState([]);
    const navigate = useNavigate();

    const handleImageUpload = (e) => {
        const files = Array.from(e.target.files);
        const remainingSlots = 20 - images.length;
        const filesToAdd = files.slice(0, remainingSlots);
        const imageUrls = filesToAdd.map(file => URL.createObjectURL(file));
        setImages([...images, ...imageUrls]);
    };

    const removeImage = (indexToRemove) => {
        setImages(images.filter((_, index) => index !== indexToRemove));
    };

    const handleSubmit = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/images-upload', {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},
                body: JSON.stringify({"images": images}),
            });
            console.log('Upload successful');
            navigate("/single-piece")
        }
        catch (err){
            console.log(err)
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-800 mb-2">
                        Upload Puzzle Pieces
                    </h1>
                    <p className="text-gray-600">Maximum puzzle size: 100 × 100 pieces</p>
                    <p className="text-gray-600 pb-4">Example image:</p>
                    <img src="/public/assets/example_photo.jpeg" alt="Example image for uploading files." className="w-130 h-74 mx-auto object-cover rounded-lg border border-gray-200"/>
                </div>

                {/* Upload Box */}
                <div className="bg-white rounded-lg shadow-md p-8 mb-6">
                    <label 
                        htmlFor="file-upload"
                        className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-gray-50 transition-colors"
                    >
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <svg className="w-12 h-12 mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <p className="mb-2 text-sm text-gray-500">
                                <span className="font-semibold">Click to upload</span> or drag and drop
                            </p>
                            <p className="text-xs text-gray-500">
                                Upload up to 20 images (PNG, JPG, JPEG) 
                            </p>
                        </div>
                        <input 
                            id="file-upload"
                            type="file" 
                            multiple 
                            accept="image/*" 
                            onChange={handleImageUpload}
                            className="hidden"
                        />
                    </label>

                    {/* Image Preview Grid */}
                    {images.length > 0 && (
                        <div className="mt-6">
                            <h3 className="text-lg font-semibold text-gray-700 mb-3">
                                Selected Images ({images.length})
                            </h3>
                            <div className="grid grid-cols-4 gap-4">
                                {images.map((img, index) => (
                                    <div key={index} className="relative group">
                                        <img 
                                            src={img} 
                                            alt={`Upload ${index + 1}`}
                                            className="w-full h-24 object-cover rounded-lg border border-gray-200"
                                        />
                                        <button
                                            onClick={() => removeImage(index)}
                                            className="absolute top-1 right-1 bg-red-500 text-black rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                                        >
                                            ×
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Submit Button */}
                <div className="text-center">
                    <button 
                        onClick={handleSubmit}
                        disabled={images.length === 0}
                        className="px-8 py-3 bg-blue-600 text-black font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                    >
                        Upload Images of Puzzle Pieces
                    </button>
                </div>
            </div>
        </div>
    )
}