var milling_3d_view = {}


milling_3d_view.createScene = function() {
    /*
     * Create a three.js scene and initialize its parameters.
     */
    var scene = new THREE.Scene();

    scene.background = new THREE.Color(0xcccccc);
    scene.fog = new THREE.FogExp2(0xcccccc, 0.0005);

    return scene;
}


milling_3d_view.createRenderer = function(containerWidth, containerHeight) {
    /*
     * Create a three.js renderer and initialize its parameters.
     */
    var renderer = new THREE.WebGLRenderer({antialias: true});

    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(containerWidth, containerHeight);

    return renderer;
}


milling_3d_view.createCamera = function(containerWidth, containerHeight) {
    /*
     * Create a three.js camera and initialize its parameters.
     */

    var camera = new THREE.PerspectiveCamera(
        60, /* camera frustum vertical field of view */
        containerWidth / containerHeight, /* camera frustum aspect ratio */
        1, /* camera frustum near plane */
        10000 /* camera frustum far plane. */
    );

    camera.position.set(
        0, /* x */
        200, /* y */
        400 /* z */
    );

    return camera;
}


milling_3d_view.createControls = function(camera, renderer) {
    /*
     * Create a three.js controls object and initialize its parameters.
     */
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.screenSpacePanning = false;
    controls.minDistance = 100;
    controls.maxDistance = 5000;
    controls.maxPolarAngle = Math.PI / 2;
    controls.rotateSpeed = 0.05;

    return controls;
}


milling_3d_view.drawCylinderBetween = function(from, to, color, diameter) {
    /*
     * Draws a cylinder between two points.
     *
     * Parameters:
     *   from: a point (with x, y and z attributes)
     *   to: a point (with x, y and z attributes)
     *   color: cylinder color
     *   diameter: cylinder diameter
     */

    var direction = new THREE.Vector3().subVectors(to, from);
    var orientation = new THREE.Matrix4();
    orientation.lookAt(from, to, new THREE.Object3D().up);
    orientation.multiply(new THREE.Matrix4().set(
        1, 0, 0, 0,
        0, 0, 1, 0,
        0, -1, 0, 0,
        0, 0, 0, 1));

    var edgeGeometry = new THREE.CylinderGeometry(diameter / 2, diameter / 2, direction.length(), 5, 1);
    var edge = new THREE.Mesh(edgeGeometry, new THREE.MeshBasicMaterial({ color: color }));
    edge.applyMatrix(orientation);

    edge.position.x = (to.x + from.x) / 2;
    edge.position.y = (to.y + from.y) / 2;
    edge.position.z = (to.z + from.z) / 2;
    return edge;
}


milling_3d_view.drawMovesOnScene = function(moves, oneMillimeterInThreejsUnits, scene, toolWidth) {
    /*
     * Draws a list of milling tool moves.
     *
     * Parameters:
     *   moves: a list of tuples: (x, y, z, if it's rapid move or milling)
     *   oneMillimeterInThreejsUnits: scaling factor, converting one millimeter to three.js units
     *   scene: the THREE.Scene object to draw on
     *   toolWidth: the width of the tool that will be used to draw moves
     */
    for (var i = 1; i < moves.length; i ++) {
        /* red color represents rapid moves, blue - actual milling */
        if (moves[i][3]) {
            color = 'red';
        } else {
            color = 'blue';
        }

        /*
         * 1/ the axes should be changed: mill Z axis is visualization Y axis and vice versa
         * 2/ the (machine) Y axis should be inverted (positive is UP)
         */
        scene.add(
            milling_3d_view.drawCylinderBetween(
                new THREE.Vector3(
                    moves[i - 1][0] * oneMillimeterInThreejsUnits,
                    moves[i - 1][2] * oneMillimeterInThreejsUnits,
                    - moves[i - 1][1] * oneMillimeterInThreejsUnits
                ),
                new THREE.Vector3(
                    moves[i][0] * oneMillimeterInThreejsUnits,
                    moves[i][2] * oneMillimeterInThreejsUnits,
                    - moves[i][1] * oneMillimeterInThreejsUnits
                ),
                color,
                toolWidth * oneMillimeterInThreejsUnits
        ));
    }
}


milling_3d_view.drawTool = function(scene) {
    /*
     * Draws the milling tool.
     */
    var toolGeometry = new THREE.CylinderBufferGeometry(3, 3, 30, 100);
    var toolMaterial = new THREE.MeshPhongMaterial({color: 0xffffff, flatShading: true});

    var mesh = new THREE.Mesh(toolGeometry, toolMaterial);
    mesh.position.x = 0;
    mesh.position.y = 15;
    mesh.position.z = 0;
    mesh.updateMatrix();
    mesh.matrixAutoUpdate = false;
    scene.add(mesh);
}


milling_3d_view.drawAxesHelper = function(scene) {
    /*
     * Draws the axes helper.
     */

    var axesHelper = new THREE.AxesHelper(100);
    scene.add(axesHelper);
}


milling_3d_view.drawGrids = function(scene, oneMillimeterInThreejsUnits) {
    /*
     * Draws two grids (small - one segment per one millineter, and big - one segment per ten millimeters).
     */
    var smallGridSegmentSize = oneMillimeterInThreejsUnits;
    var smallGridNumSegments = 100;
    var smallGridHelper = new THREE.GridHelper(smallGridSegmentSize * smallGridNumSegments, smallGridNumSegments);
    scene.add(smallGridHelper);

    var bigGridSegmentSize = oneMillimeterInThreejsUnits * 10;
    var bigGridNumSegments = 10;
    var bigGridHelper = new THREE.GridHelper(bigGridSegmentSize * bigGridNumSegments, bigGridNumSegments, 'red', 'red');
    scene.add(bigGridHelper);
}


milling_3d_view.initializeLights = function(scene) {
    /*
     * Adds lights to the scene.
     */
    var light = new THREE.DirectionalLight(0xffffff);
    light.position.set(1, 1, 1);
    scene.add(light);

    var light = new THREE.DirectionalLight(0x002288);
    light.position.set(- 1, - 1, - 1);
    scene.add(light);

    var light = new THREE.AmbientLight(0x222222);
    scene.add(light);
}


milling_3d_view.initializeWindowResizeHandler = function(camera, container, renderer) {
    /*
     * Initializes a window resize handler that updates camera and renderer parameters
     * according to the new container sizes computed from the window size.
     */

    function onWindowResize() {
        var width = container.clientWidth;
        var height = container.clientHeight;

        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }

    window.addEventListener('resize', onWindowResize, false);
}


milling_3d_view.initializeAnimation = function(camera, controls, scene, renderer) {
    /*
     * Initializes rendering to be performed on each animation frame.
     */

    function animationStep() {
        requestAnimationFrame(animationStep);
        controls.update();
        renderer.render(scene, camera);
    }

    animationStep();
}


milling_3d_view.visualizeMoves = function(container, moves, toolWidth) {
    /*
     * Actually visualize milling tool moves in a HTML container.
     *
     * Parameters:
     *   container: a HTML container the 3d visualization will be shown in
     *   moves: a list of tuples: (x, y, z, if it's rapid move or milling)
     *   toolWidth: the width of the tool that will be used to draw moves
     */
    var oneMillimeterInThreejsUnits = 10;

    if (WEBGL.isWebGLAvailable() === false) {
        document.body.appendChild(WEBGL.getWebGLErrorMessage());
    }

    var containerWidth = container.clientWidth;
    var containerHeight = container.clientHeight;

    var scene = milling_3d_view.createScene();
    var renderer = milling_3d_view.createRenderer(containerWidth, containerHeight);
    var camera = milling_3d_view.createCamera(containerWidth, containerHeight);
    var controls = milling_3d_view.createControls(camera, renderer);

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    milling_3d_view.drawMovesOnScene(moves, oneMillimeterInThreejsUnits, scene, toolWidth);
    milling_3d_view.drawTool(scene);
    milling_3d_view.drawAxesHelper(scene);
    milling_3d_view.drawGrids(scene, oneMillimeterInThreejsUnits);

    milling_3d_view.initializeLights(scene);
    milling_3d_view.initializeWindowResizeHandler(camera, container, renderer);
    milling_3d_view.initializeAnimation(camera, controls, scene, renderer);
}
