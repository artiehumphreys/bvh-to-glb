# bvh-to-glb
Transform your BVH files into interactive animations effortlessly with BVH-to-GLB. This tool uses the Blender API to convert .bvh files into .glb format, making it easy to integrate motion capture data into 3D environments. Using this repository is incredibly simple:
### 1. Clone the repository
```bash
git clone https://github.com/artiehumphreys/bvh-to-glb
cd bvh-to-glb/
```
### 2. Run the shell script
```bash
source run.sh
```
That's it! The script will ensure all dependencies are properly handled.
## Other Notes
### Customizing the Shell Script
You can edit the provided shell script to ensure it points to the correct directories containing your .bvh files. Modify the paths in `run.sh` to match your folder structure for seamless operation.

### Adding a Backdrop or Floor
To include a backdrop or floor for your animation, create an object and save it as `rendering/court.obj` within the working directory. This object will be imported and used as the backdrop or floor in your animations.

## Video Demo
This demo was created using my own backdrop and BVH data. If you'd like to use your own data, look [here](#other-notes).
https://github.com/user-attachments/assets/0dc799c0-190a-4536-bc96-f1d7aeb63a03


