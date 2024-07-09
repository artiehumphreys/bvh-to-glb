import bpy  # type: ignore
import os
import mathutils # type: ignore
from pathlib import Path

class bvh_to_glb:
    def __init__(self, output_path = "babylon_viewer/output"):
        self.output_path = output_path
        self.filename = ""
        self.player_ids: dict[int, str] = {}
        self.teams: set[str] = set()
        self.scale = 1.25

    def process_teams_ids(self):
        split = self.filename.split('_')[1]
        if not split[1] in self.teams:
            self.teams.add(split[1])
        self.player_ids[split[2]] = ""

    # def read_csv(self,file = r"players 1.csv"):

    def create_sphere_at_bone(self, bone, armature):
        if bone.name == 'lWrist' or bone.name == 'rWrist':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=bone.head_radius / self.scale, location=bone.head_local)
            sphere = bpy.context.object
            sphere.scale = ((bone.head_local - bone.tail_local).length * 10, 1, 1)
        else:    
            bpy.ops.mesh.primitive_uv_sphere_add(radius=bone.head_radius, location=bone.head_local)
        sphere = bpy.context.object
        sphere.name = f"sphere_{bone.name}_{self.filename}"
        if bone.name == 'baseHead':
            head_height = 0.15
            sphere.location += mathutils.Vector((0, 0, head_height))
            sphere.scale = (self.scale, self.scale, self.scale)

        mod = sphere.modifiers.new(name="Armature", type="ARMATURE")
        mod.object = armature
        sphere.parent = armature
        sphere.parent_type = "BONE"
        sphere.parent_bone = bone.name


    def create_cone_arm(self, bone, armature):
        parent = bone.parent

        cone_vector = bone.head_local - parent.head_local
        cone_length = cone_vector.length
        cone_direction = cone_vector.normalized()

        cone_midpoint_world = (parent.head_local + bone.head_local) / 2

        bpy.ops.mesh.primitive_cone_add(radius1=bone.head_radius / self.scale, radius2=bone.tail_radius / self.scale, depth=cone_length, location=cone_midpoint_world)
        cone = bpy.context.object
        cone.name = f"Cone_{parent.name}_to_{bone.name}_{self.filename}"

        rotation = cone_direction.to_track_quat('Z', 'Y').to_euler()
        cone.rotation_euler = rotation

        cone.parent = armature
        cone.parent_type = "BONE"
        cone.parent_bone = parent.name


    def convert_bvh_to_glb(self, directory, output_name):
        bpy.ops.wm.read_factory_settings(use_empty=True)

        bpy.ops.wm.obj_import(filepath="Basketball_court.obj")

        for file in os.listdir(directory):
            if not file.endswith(".bvh"):
                continue
            self.filename = Path(file).stem
            self.process_teams_ids()

            bvh_path = os.path.join(directory, file)
            bpy.ops.import_anim.bvh(filepath=bvh_path)
            bpy.context.scene.render.fps = 60

            armature = bpy.context.object
            if armature.type != "ARMATURE":
                continue
            bpy.context.view_layer.objects.active = armature

            for bone in armature.pose.bones:
                bone.bone.use_local_location = True
                bone.bone.use_relative_parent = True
                self.create_sphere_at_bone(bone.bone, armature)
                if bone.bone.parent:
                    self.create_cone_arm(bone.bone, armature)

        bpy.ops.object.select_all(action="SELECT")

        bpy.ops.export_scene.gltf(filepath=output_name, export_format="GLB")


if __name__ == "__main__":
    converter = bvh_to_glb()
    converter.convert_bvh_to_glb("output_BVH", converter.output_path)