const canvas = document.getElementById("renderCanvas");

const engine = new BABYLON.Engine(canvas);

const createScene = () => {
    const fileName = "Pose3D_BKN_UTA.glb";
    const scene = new BABYLON.Scene(engine);
    console.log(`Loading model: ${fileName}`);
    let camera = null;

    BABYLON.SceneLoader.Append("", fileName, scene, function(scene) {
        console.log("Model loaded successfully.");

        let headNode = null;
        scene.meshes.forEach(mesh => {
            if (mesh.name.toLowerCase().includes("head")) {
                headNode = mesh;
            }
        });
        if (!headNode) {
            console.error("Head node not found in the scene.");
            return;
        }
        console.log(`Head node found: ${headNode.name}`);

        camera = new BABYLON.TargetCamera("camera1", new BABYLON.Vector3(0, 1, 5), scene);
        camera.parent = headNode;
        camera.setTarget(headNode.getAbsolutePosition());
        camera.attachControl(canvas, true);
        const light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(1, 1, 0), scene);

        scene.animationGroups.forEach((group) => {
            group.start(true);
        });

        engine.runRenderLoop(() => {
            scene.render();
        });

    });

    return scene;
};

const scene = createScene();