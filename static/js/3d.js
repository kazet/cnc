function cylinderBetween(from, to, color, width) {
    var direction = new THREE.Vector3().subVectors(to, from);
    var orientation = new THREE.Matrix4();
    orientation.lookAt(from, to, new THREE.Object3D().up);
    orientation.multiply(new THREE.Matrix4().set(
        1, 0, 0, 0,
        0, 0, 1, 0,
        0, -1, 0, 0,
        0, 0, 0, 1));

    var edgeGeometry = new THREE.CylinderGeometry(width, width, direction.length(), 5, 1);
    var edge = new THREE.Mesh(edgeGeometry, new THREE.MeshBasicMaterial({ color: color }));
    edge.applyMatrix(orientation);

    // position based on midpoints - there may be a better solution than this
    edge.position.x = (to.x + from.x) / 2;
    edge.position.y = (to.y + from.y) / 2;
    edge.position.z = (to.z + from.z) / 2;
    return edge;
}

function initialize3dVisualization(container, moves, toolWidth) {
    var scale = 10;

    container.innerHTML = '';

    if (WEBGL.isWebGLAvailable() === false) {
        document.body.appendChild(WEBGL.getWebGLErrorMessage());
    }

    var camera, controls, scene, renderer;
    var width = container.clientWidth;
    var height = container.clientHeight;

    init();
    animate();

    function init() {
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xcccccc);
        scene.fog = new THREE.FogExp2(0xcccccc, 0.0005);
        
        renderer = new THREE.WebGLRenderer({antialias: true});
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(width, height);
        container.appendChild(renderer.domElement);
        camera = new THREE.PerspectiveCamera(60, width / height, 1, 10000);
        camera.position.set(0, 200, 400);

        // controls
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.25;
        controls.screenSpacePanning = false;
        controls.minDistance = 100;
        controls.maxDistance = 5000;
        controls.maxPolarAngle = Math.PI / 2;
        controls.rotateSpeed = 0.05;

        // world
        for (var i = 1; i < moves.length; i ++) {
            /*
             * 1/ the axes should be changed: mill Z axis is visualization Y axis and vice versa
             * 2/ the (machine) Y axis should be inverted (positive is UP)
             */
            scene.add(
                cylinderBetween(
                    new THREE.Vector3(
                        moves[i - 1][0] * scale,
                        moves[i - 1][2] * scale,
                        - moves[i - 1][1] * scale
                    ),
                    new THREE.Vector3(
                        moves[i][0] * scale,
                        moves[i][2] * scale,
                        - moves[i][1] * scale
                    ),
                    'red',
                    toolWidth * scale
            ));
        }

        var toolGeometry = new THREE.CylinderBufferGeometry(3, 3, 30, 100);
        var toolMaterial = new THREE.MeshPhongMaterial({color: 0xffffff, flatShading: true});

        var mesh = new THREE.Mesh(toolGeometry, toolMaterial);
        mesh.position.x = 0;
        mesh.position.y = 15;
        mesh.position.z = 0;
        mesh.updateMatrix();
        mesh.matrixAutoUpdate = false;
        scene.add(mesh);

        var axesHelper = new THREE.AxesHelper(100);
        scene.add(axesHelper);
        
        var smallGridSegmentSize = scale;
        var smallGridNumSegments = 100;
        var smallGridHelper = new THREE.GridHelper(smallGridSegmentSize * smallGridNumSegments, smallGridNumSegments);
        scene.add(smallGridHelper);

        var bigGridSegmentSize = scale * 10;
        var bigGridNumSegments = 10;
        var bigGridHelper = new THREE.GridHelper(bigGridSegmentSize * bigGridNumSegments, bigGridNumSegments, 'red', 'red');
        scene.add(bigGridHelper);

        // lights
        var light = new THREE.DirectionalLight(0xffffff);
        light.position.set(1, 1, 1);
        scene.add(light);
        var light = new THREE.DirectionalLight(0x002288);
        light.position.set(- 1, - 1, - 1);
        scene.add(light);
        var light = new THREE.AmbientLight(0x222222);
        scene.add(light);

        window.addEventListener('resize', onWindowResize, false);
    }

    function onWindowResize() {
        var width = container.clientWidth;
        var height = container.clientHeight;

        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        render();
    }

    function render() {
        renderer.render(scene, camera);
    }
}
