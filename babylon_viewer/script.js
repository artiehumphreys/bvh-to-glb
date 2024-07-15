const canvas = document.getElementById("renderCanvas");

const engine = new BABYLON.Engine(canvas);

let num = 0;

let isPaused = false;

let frame = 0;

const createScene = () => {
    const fileName = "Pose3D_BKN_UTA.glb";
    const scene = new BABYLON.Scene(engine);
    console.log(`Loading model: ${fileName}`);
    let camera = null;

    BABYLON.SceneLoader.Append("", fileName, scene, function(scene) {
        let headNode = findHead(scene, num);
        let name = headNode?.name?.split('_')[2] ?? "Default";
        displayName(name);
        if (headNode === null){
            camera = new BABYLON.ArcRotateCamera("camera1", -Math.PI / 2, Math.PI / 2, 2, new BABYLON.Vector3(0, 1, 0), scene);
            scene.createDefaultCameraOrLight(true, true, true);

        } else {
            camera = new BABYLON.TargetCamera("camera1", new BABYLON.Vector3(0, 0, -3), scene);
            camera.parent = headNode;
            camera.setTarget(headNode.getAbsolutePosition());
        }  
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
    cameraHeads = scene.meshes.filter(node => node.name.includes("sphere_baseHead"));
    cameraHeads.unshift(null);
    if (cameraHeads.length === 1) {
        console.error("Head node not found in the scene.");
        return;
    }
    num ++;
    if (num >= cameraHeads.length){
        num = 1;
    }
    return cameraHeads[num-1]
}

function displayName(name){
    nametag = document.getElementById("nametag");
    nametag.innerHTML = name;
}

window.addEventListener("keydown", function(e){
    if (e.code === "KeyC"){
        createScene();
    }
    if (e.code === "Space"){
        isPaused = true;
        scene.animationGroups.forEach((group) => {
            group.pause();
        });
    }
});

window.addEventListener("keyup", function(e) {
    if (e.code === "Space") {
        isPaused = false;
        engine.runRenderLoop(() => {
            if (!isPaused){
                scene.render();
            }
        });
        scene.animationGroups.forEach((group) => {
            group.play(true);
        });
    }
});
const slider = document.getElementById("slider");
slider.onchange = function() {
    isPaused = false;
    scene.animationGroups.forEach((group) => {
        group.play();
    });
}
slider.oninput = function() {
    isPaused = true;
    scene.animationGroups.forEach((group) => {
        group.pause();
    });
    maxFrame = scene.animationGroups[0].to;
    frame = Math.floor(this.value / 100 * maxFrame); 
    scene.animationGroups.forEach((group) => {
        group.goToFrame(frame);
    });
}


const scene = createScene();
