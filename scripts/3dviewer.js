function init3DViewer(modelPath, viewerId) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setClearColor(0x111111, 1);
    const viewer = document.getElementById(viewerId);
    if (!viewer) {
        console.error('Viewer element not found');
        return;
    }
    renderer.setSize(viewer.clientWidth, viewer.clientWidth);
    viewer.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    camera.position.set(5, 5, 30);
    controls.update();

    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    const loader = new THREE.GLTFLoader();
    const objLoader = new THREE.OBJLoader();
    const mtlLoader = new THREE.MTLLoader();

    if (modelPath.endsWith('.gltf') || modelPath.endsWith('.glb')) {
        loader.load(modelPath, function(gltf) {
            scene.add(gltf.scene);
            // Center the model
            const box = new THREE.Box3().setFromObject(gltf.scene);
            const center = box.getCenter(new THREE.Vector3());
            gltf.scene.position.sub(center);
        }, undefined, function(error) {
            console.error('An error happened loading the GLTF:', error);
        });
    } else if (modelPath.endsWith('.obj')) {
        const mtlPath = modelPath.replace('.obj', '.mtl');
        mtlLoader.load(mtlPath, function(materials) {
            materials.preload();
            objLoader.setMaterials(materials);
            objLoader.load(modelPath, function(object) {
                scene.add(object);
                // Center the model
                const box = new THREE.Box3().setFromObject(object);
                const center = box.getCenter(new THREE.Vector3());
                object.position.sub(center);
            }, undefined, function(error) {
                console.error('An error happened loading the OBJ:', error);
            });
        }, undefined, function(error) {
            console.error('An error happened loading the MTL:', error);
        });
    } else {
        console.error('Unsupported file format. Use GLTF/GLB or OBJ with MTL.');
    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    function updateSize() {
        const width = viewer.clientWidth;
        renderer.setSize(width, width);
    }
    window.addEventListener('resize', updateSize);
}