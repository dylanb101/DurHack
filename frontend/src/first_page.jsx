
// This page is for uploading images in the correct format, to then be used to build the puzzle.

import { useState } from "react"
import { useNavigate } from "react-router-dom";


export default function FirstPage(){

    const [images, setImages] = useState([]);
    const navigate = useNavigate();

    const handleImageUpload = (e) => {
        const files = Array.from(e.target.files).slice(0, 20);
        const imageUrls = files.map(file => URL.createObjectURL(file));
        setImages(imageUrls);
    };

    const handleSubmit = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/images-upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({"images": images}),
            });
            navigate("/single-piece")
        }
        catch (err){
            console.log(err)
        }
    };

    return (
        <div>
            <h1>Max 100 by 100</h1>
            <input type="file" className="hidden" multiple accept="image/*" onChange={handleImageUpload} />
            <button onClick={handleSubmit}>
                Upload images of puzzle pieces.
            </button>
        </div>
    )
}