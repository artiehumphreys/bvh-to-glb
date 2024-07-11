const canvas = document.getElementById("renderCanvas");

const engine = new BABYLON.Engine(canvas);

let num = 0;

const createScene = () => {
    const fileName = "Pose3D_BKN_UTA.glb";
    const scene = new BABYLON.Scene(engine);
    console.log(`Loading model: ${fileName}`);
    let camera = null;

    BABYLON.SceneLoader.Append("", fileName, scene, function(scene) {
        let headNode = findHead(scene, num);
        camera = new BABYLON.TargetCamera("camera1", new BABYLON.Vector3(0, 1, -3), scene);
        camera.parent = headNode;
        camera.rotation = new BABYLON.Vector3(0, 0, 0);
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

function findHead(scene){
    let headNodes = [];
    let headNode = null;
    console.log(scene.meshes)
    scene.meshes.forEach(mesh => {
            if (mesh.name.toLowerCase().includes("head")) {
                headNode = mesh
                headNodes.push(headNode);
            }
        });
        if (!headNode) {
            console.error("Head node not found in the scene.");
            return;
        }
    num ++;
    return headNodes[num-1]
}

window.addEventListener("keydown", function(e){
    if (e.code === "Space"){
        num ++;
        createScene();
    }
});

const scene = createScene();
