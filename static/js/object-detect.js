
const video = document.getElementById('camera');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Load the Edge Impulse model
async function loadModel() {
    const model = await tf.loadGraphModel('/models/model.json');
    console.log('Model loaded successfully');
    return model;
}

// Access the camera
async function startCamera() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        detectObjects();
    };
}

// Perform object detection
async function detectObjects() {
    const model = await loadModel();

    async function detectFrame() {
        const tfImg = tf.browser.fromPixels(video).expandDims(0).toFloat();
        const predictions = await model.executeAsync(tfImg);

        // Clear canvas and draw results
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        predictions.forEach(pred => {
            const [x, y, width, height] = pred.bbox;
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, width, height);
            ctx.fillText(pred.class, x, y > 10 ? y - 5 : y + 15);
        });

        requestAnimationFrame(detectFrame);
    }

    detectFrame();
}

startCamera();